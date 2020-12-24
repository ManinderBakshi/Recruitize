from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, IntegerField, TextAreaField, DateTimeField, SelectField
from wtforms.validators import DataRequired, ValidationError, Length
from app.model import User
from flask import request


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class demographic_form(FlaskForm):
    first_name = StringField('Enter first name',
                             validators=[DataRequired(),
                             Length(min=1, max=100)])

    last_name = StringField('Enter last name', 
                            validators=[DataRequired(), Length(min=1, max=100)])

    position = StringField('Enter your Positon',
                            validators=[DataRequired()])

    gender = SelectField('Specifiy your gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Rather Not Say', 'Rather Not Say')],
                         validators=[DataRequired(), Length(min=1, max=10)])

    nationality = StringField('Specifiy your nationality',
                              validators=[DataRequired(),
                               Length(min=1, max=10)])


    dob = StringField('Enter your Date of Birth', validators=[DataRequired()])

    submit = SubmitField('Submit Demographic details')


class contact_form(FlaskForm):
    address = StringField('Enter address', validators=[DataRequired()])

    phone_no = StringField('Enter phone number', validators=[DataRequired()])

    linkedin_prof = StringField('Enter Linkedin Profile',
                                validators=[DataRequired()])

    email = StringField('Enter email id', validators=[DataRequired()])

    submit = SubmitField('Submit Contact details')


class highest_qualification_form(FlaskForm):
    course = StringField('Enter Course Name', validators=[DataRequired(),
                         Length(min=1, max=100)])
    
    institution = StringField('Enter name of Instution', validators=[DataRequired()])

    year = IntegerField('Passout year', validators=[DataRequired()])

    percentage = FloatField('Marks obtained', validators=[DataRequired()])

    subjects = TextAreaField('Stream or Main subjects',
                           validators=[DataRequired(), Length(min=1, max=100)])

    submit = SubmitField('Submit Highest Qualification')


class qualification_form(FlaskForm):
    course = StringField('Enter Course Name', validators=[DataRequired(),
                         Length(min=1, max=100)])
    
    college = StringField('Enter name of Instution', validators=[DataRequired()])

    year = IntegerField('Passout year', validators=[DataRequired()])

    percentage = FloatField('Marks obtained', validators=[DataRequired()])

    subjects = TextAreaField('Stream or Main subjects',
                             validators=[DataRequired(), Length(min=1, max=100)])

    submit = SubmitField('Submit Qualification')


class certification_form(FlaskForm):
    course = StringField('Enter name of course')

    organization = StringField('Enter name of Organization',
                               validators=[Length(min=1, max=100)])

    credentials = TextAreaField('Enter certificate number',
                                validators=[Length(min=1, max=100)])

    submit = SubmitField('Submit Certification')


class project_form(FlaskForm):
    project_Name = StringField('Enter Name of your project')

    project_details = TextAreaField('Enter details of project',
                                    validators=[Length(min=1, max=50)])

    year = IntegerField('Project Year')

    submit = SubmitField('Submit')


class experience_form(FlaskForm):
    organization_name = StringField('Enter Name of organization',
                                    validators=[Length(min=1, max=100)])

    position = StringField('Enter your position in organization',
                           validators=[Length(min=1, max=50)])

    duration_in_months = IntegerField('Enter work duration in months')

    details = StringField('Enter details about your work')

    submit = SubmitField('Submit experience')


class other_details_forms(FlaskForm):
    other_details = TextAreaField('Tell us about yourself ')

    skills = StringField('Enter your skills , separated by commas')

    profile = StringField('Enter your professinal summary or profile')

    submit = SubmitField('Submit details')