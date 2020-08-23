""" SQLAlchemy models for Burijji Chat App """

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """ Connect to database """

    db.app = app
    db.init_app(app)

class User(db.Model):
    """ User Model """
    __tablename__="users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    
    username = db.Column(db.String(20),
                   nullable = False,
                   unique = True)

    password = db.Column(db.Text,
                   nullable = False)

    first_name = db.Column(db.String(15),
                   nullable = False)

    last_name = db.Column(db.String(15),
                   nullable = False)

    email = db.Column(db.String(30),
                   nullable = False)

    preferred_language = db.Column(db.String(30),
                   db.ForeignKey("languages.name"))

    chatrooms = db.relationship("Chatroom",
                   secondary="memberships",
                   backref="users")

    messages = db.relationship("Message")

    @classmethod
    def register(cls, first_name, last_name, username, password, email, preferred_language):
        """ Formats user data and hashes sensitive info so that it's suitable to store in database. Returns user"""
       
        hashed = bcrypt.generate_password_hash(password)

        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")
        
        # returns user instance of user with hashed password
        return cls(username=username, password=hashed_utf8, email= email, first_name=first_name, last_name=last_name, preferred_language=preferred_language)
    
    @classmethod
    def authenticate(cls, username, password):
        """ Validates that user exists in db & password is correct. Returns user instance if authenticated or False if not"""

        found_user = User.query.filter_by(username=username).first()

        if found_user and bcrypt.check_password_hash(found_user.password, password):
            return found_user
        else :
            return False


class Language(db.Model):
    """ Language Model """
    __tablename__="languages"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    
    name = db.Column(db.String(20),
                   nullable=False,
                   unique=True)


class Chatroom(db.Model):
    """ Chatroom Model """
    __tablename__="chatrooms"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    roomcode = db.Column (db.String(11),
                   nullable=False,
                   unique=True)
    
    name = db.Column(db.String(20),
                   nullable=False)

    messages = db.relationship("Message")


class Membership(db.Model):
    """ Memberships Model connecting users to chatrooms """
    __tablename__="memberships"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    user_id = db.Column(db.Integer,
                   db.ForeignKey("users.id"))  # Add ondelete cascade

    chatroom_id = db.Column(db.Integer,
                   db.ForeignKey("chatrooms.id")) # Add ondelete cascade

    is_admin = db.Column(db.Boolean,
                   nullable=False,
                   default=True)


class Message(db.Model):
    """ Message Model """
    __tablename__="messages"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    content = db.Column(db.Text,
                   nullable=False)

    user_id = db.Column(db.Integer,
                   db.ForeignKey("users.id")) # Add ondelete cascade

    chatroom_id = db.Column(db.Integer,
                   db.ForeignKey("chatrooms.id"))  # Add ondelete cascade

    language_id = db.Column(db.Integer,
                   db.ForeignKey("languages.id"))

    timestamp = db.Column(db.String(20),
                   nullable=False,
                   default=datetime.utcnow())

    is_translated = db.Column(db.Boolean,
                    nullable=False,
                    default=False)
    
    chatroom = db.relationship("Chatroom") #Allows SQLAlchemy to 'navigate' the connection

    user = db.relationship("User")




