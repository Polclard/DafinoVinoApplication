from enum import Enum
from flask_login import UserMixin
from __init__ import db


class UserRole(Enum):
    ADMIN = 'admin'
    USER = 'user'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
