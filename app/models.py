from app import db

from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
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
