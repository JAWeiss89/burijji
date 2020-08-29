from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired

class RegisterForm(FlaskForm):
    """ Form to register a new user """

    first_name = StringField("First Name:", validators=[InputRequired(message="This field cannot be left blank")])
    last_name = StringField("Last Name:", validators=[InputRequired(message="This field cannot be left blank")])
    username = StringField("Username:", validators=[InputRequired(message="This field cannot be left blank")])
    password = PasswordField("Password:", validators=[InputRequired(message="This field cannot be left blank")])
    email = StringField("Email:", validators=[InputRequired(message="This field cannot be left blank")])
    preferred_language = SelectField("Preferred Language:", choices=[('english', 'English'), ('spanish', 'Español'), ('portuguese', 'Português')])


class LoginForm(FlaskForm):
    """ Form to log in existing user """

    username = StringField("Username:", validators=[InputRequired(message="This field cannot be left blank")])
    password = PasswordField("Password:", validators=[InputRequired(message="This field cannot be left blank")])


class ChatroomForm(FlaskForm):
    """ Form to create new chatroom """

    name = StringField("Name of Chatroom", validators=[InputRequired(message="This field cannot be left blank")])
    roomcode = StringField("Room Code", validators=[InputRequired(message="This field cannot be left blank")])