from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from varkapp.models import User

class RegistrationForm(FlaskForm):
    gender = RadioField('Gender',
                            choices=[('M','Male'),('FM','Female')])
    firstname = StringField('First Name',
                            validators=[DataRequired(), Length(min=5, max=50)])
    lastname = StringField('Last Name',
                            validators=[DataRequired(), Length(min=5, max=50)])
    age = StringField('Age',
                            validators=[DataRequired(), Length(min=1, max=2)])
    email = StringField('Email',
                            validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

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