from collections import namedtuple
from sqlalchemy.orm import backref, lazyload
from app import db

from flask import url_for
from flask import current_app

from werkzeug.security import generate_password_hash, check_password_hash
# for token
import base64
from datetime import datetime, timedelta
import os

import redis
import rq


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        """ produces a dictionary with the user collection representation

        Args:
            query (object): a Flask-SQLAlchemy query object.
            page (int): a page number.
            per_page (int): a page size.
                The first 3 args that determine what are the items that are going to be returned.
            endpoint ([type]): [description]

        Returns:
            [type]: [description]
        """
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(PaginatedAPIMixin, db.Model,):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    # many to many relationship. From part viii
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    # add task relationship
    tasks = db.relationship('Task', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def launch_task(self, name, description, *args, **kwargs):
        # enqueue the task from the `tasks.py`
        # NOTE: launch_task() adds the new task object to the session, but it does not issue a commit. 
        rq_job = current_app.task_queue.enqueue('app.tasks.' + name, self.id,
                                                *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description,
                    user=self)
        db.session.add(task)
        return task


    def get_task_in_progress(self):
        """returns the complete list of functions that are outstanding for the user.
            This method is for preventing users from starting two or more tasks
            of the same type concurrently, so before I launch a task, I can use
            this method to find out if a previous task is currently running.
        Returns:
            Task: Task objects.
        """
        return Task.query.filter_by(user=self, complete=False).all()


    def get_task_in_progress(self, name):
        """return the task object by the task name

        Args:
            name (string): the unique task name.

        Returns:
            Task: task object
        """
        return Task.query.filter_by(name=name, user=self, complete=False).first


    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token


    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)


    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    
    def to_dict(self):
        """converts a user object to a Python representation,
            which will then be converted to JSON. 

        Returns:
            dict: the data represent the user object.
        """
        data = {
            'id': self.id,
            'username': self.username,
            '_links': {
                'self': url_for('api.get_user', id=self.id)
            }
        }

        return data


    def from_dict(self, data, new_user=False):
        """the reverse direction of to_dict function.
            convert the data to a User object.

        Args:
            data (dict): containing user info.
        """
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])


    def __repr__(self):
        return '<User {}>'.format(self.username)


class Task(db.Model):
    """
    The model is going to store the task's fully qualified name (as passed to RQ),
    a description for the task that is appropriate for showing to users,
    a relationship to the user that requested the task,
    and a boolean that indicates if the task completed or not. 
    """
    # NOTE: the ids are the string-type job identifiers generated by RQ.
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job


    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100
