from flask_wtf import FlaskForm
from wtforms import StringField, TextField, PasswordField
from wtforms.validators import InputRequired, Email, Length

class RegisterForm(FlaskForm):
    '''registration form'''
    username = StringField('Username', validators = [InputRequired('Username required.'), Length(max=20, message='Username must be less than 20 characters.')])

    password = PasswordField('Password', validators = [InputRequired('Password required.')])

    email = StringField('Email', validators = [InputRequired('Email required.'), Email(message='Not a valid email'), Length(max=50, message='Email must be less than 20 characters.')])

    first_name = StringField('First Name', validators = [InputRequired('First name required.'), Length(max=30, message='First name must be less than 30 characters.')])

    last_name = StringField('Last Name', validators = [InputRequired('Last name required.'), Length(max=30, message='Last name must be less than 30 characters.')])


class LoginForm(FlaskForm):
    '''login form'''
    username = StringField('Username', validators = [InputRequired('Username required.')])

    password = PasswordField('Password', validators = [InputRequired('Password required.')])



