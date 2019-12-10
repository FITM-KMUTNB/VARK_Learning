from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class InsertSubject(FlaskForm):
    
    subject = StringField('Subject',
                           validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Submit')

class InsertContent(FlaskForm):
    
    pretest = FileField('Pretest', validators=[FileAllowed(['PDF'])])
    chapter = StringField('Chapter',
                            validators=[DataRequired()])
    topic = StringField('Topic',
                            validators=[DataRequired()])
    excercise = StringField('Exercise',
                            validators=[DataRequired()])
    posttest = StringField('Posttest',
                            validators=[DataRequired()])

    submit = SubmitField('Submit')

class InsertChapter(FlaskForm):
    chapter = StringField('Chapter', validators=[DataRequired(), Length(min=2, max=20)])
    chapternumber = IntegerField('No.', validators=[DataRequired()])