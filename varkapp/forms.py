from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from varkapp.models import User

class RegistrationForm(FlaskForm):
    studentid = StringField('Student ID',
                           validators=[DataRequired(), Length(min=13, max=13)])
    firstname = StringField('First Name',
                           validators=[DataRequired(), Length(min=5, max=50)])
    lastname = StringField('Last Name',
                            validators=[DataRequired(), Length(min=5, max=50)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_studentid(self, studentid):
        user = User.query.filter_by(studentid=studentid.data).first()
        if user:
            raise ValidationError("That student id is taken. Please choose a different one.")
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')