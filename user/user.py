from werkzeug.security import check_password_hash, generate_password_hash
from server import app
from datetime import datetime
from bson import json_util

class User():

    def __init__(self, id):
        self.username = None
        self.email = None
        self.id = id
        self.password_hash = None

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def set_email(self, email):
        self.email = email

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)

    @staticmethod
    def build_user(user):
        userObj = User(json_util.dumps(user['_id']))
        userObj.username = user['username']
        userObj.email = user['email']
        userObj.password_hash = user['password_hash']
        return userObj

    def save(self):
        self.id = app.mongo.db.user.insert({
                "username": self.username,
                "password_hash": self.password_hash,
                "email": self.email,
                "createtedAt": datetime.now()
            })
        if self.id:
            return True
        else:
            return False