from app import db

from flask import url_for

from werkzeug.security import generate_password_hash, check_password_hash


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

class User(PaginatedAPIMixin, db.Model,):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    
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
        pass


    def __repr__(self):
        return '<User {}>'.format(self.username)
