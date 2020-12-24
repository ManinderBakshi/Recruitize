from hashlib import md5
from app import db , login
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from flask import Flask 
from time import time
import jwt
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

app = Flask(__name__)


class User(UserMixin, db.Model):
	__tablename__ = "user"
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	recruiter = db.Column(db.Boolean())
	Resume = db.relationship('Resume', backref='author', lazy='dynamic', cascade='all, delete-orphan')
	JD = db.relationship('JD', backref='author', lazy='dynamic', cascade='all, delete-orphan')
	Demographic_details = db.relationship('Demographic_details', 
										backref='author', lazy='dynamic',
		                                cascade="all, delete-orphan")
	Contact_details = db.relationship('Contact_details', backref='author',
		                               lazy='dynamic', cascade='all, delete-orphan')
	highest_qualification = db.relationship('Highest_qualification', backref='author',
									lazy='dynamic', cascade='all, delete-orphan')
	Qualifications = db.relationship('Qualifications', backref='author',
									lazy='dynamic', cascade='all, delete-orphan')
	Certifications = db.relationship('Certifications', backref='author',
									lazy='dynamic', cascade='all, delete-orphan')
	Projects = db.relationship('Projects', backref='author',
									lazy='dynamic', cascade='all, delete-orphan')
	Experience = db.relationship('Experience', backref='author',
									lazy='dynamic', cascade='all, delete-orphan')
	Other_details = db.relationship('Other_details', backref='author',
									lazy='dynamic', cascade='all, delete-orphan')


   

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self,password):
		self.password_hash = generate_password_hash(password)

	def check_password(self,password):
		return check_password_hash(self.password_hash,password)
	
	def get_reset_password_token(self, expires_in=600):
		return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            "recruitize", algorithm='HS256').decode('utf-8')

	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, "recruitize",
                            algorithms=['HS256'])['reset_password']
		except:
			return
		return User.query.get(id)

	def to_dict(self):
		data = {
			'id':self.id,
			'username':self.username,
			'email': self.email,
			'recruiter': self.recruiter
		}
		return data

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

class Demographic_details(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	first_name = db.Column(db.String(64))
	last_name = db.Column(db.String(64))
	position = db.Column(db.String(64))
	dob = db.Column(db.String(64))
	nationality = db.Column(db.String(64))
	gender = db.Column(db.String(64))
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Demographic details:First-Name {} '.format(self.first_name)

	def to_dict(self):
		data = {
			'id' : self.id,
			'first_name': self.first_name,
			'last_name':self.last_name,
			'position': self.position,
			'dob' : self.dob,
			'nationality': self.nationality,
			'gender':self.gender,
			'user_id':self.user_id
		}
		return data


class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.Text())
    graph = db.Column(db.Text())
    wcloudname = db.Column(db.Text())
    position = db.Column(db.String(120))
    filename = db.Column(db.Text())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Resume Path: Path {}'.format(self.path)

    def to_dict(self):
        data = {
			'id': self.id,
			'path': self.path,
			'graph': self.graph,
			'wcloudname': self.wcloudname,
			'filename': self.filename,
			'position': self.position,
			'user_id': self.user_id
		}
        return data


class JD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.Text())
    position = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<JD Path: Path {}'.format(self.path)

    def to_dict(self):
        data = {
			'id': self.id,
			'details': self.details,
			'position': self.position,
			'user_id': self.user_id
		}
        return data


class Contact_details(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	email = db.Column(db.String(120))
	phone_no = db.Column(db.String(20))
	linkedin_prof = db.Column(db.String(200))
	address = db.Column(db.String(200))
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Contact details: E-Mail {} '.format(self.email)

	def to_dict(self):
		data = {
			'id' : self.id,
			'email': self.email,
			'phone_no':self.phone_no,
			'linkedin_prof' : self.linkedin_prof,
			'address': self.address,
			'user_id':self.user_id
		}
		return data

class Highest_qualification(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	course = db.Column(db.String(120))
	institution = db.Column(db.String(150))
	year = db.Column(db.Integer())
	percentage = db.Column(db.Float())
	subjects = db.Column(db.Text())
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Highest_Qualification_details: Course {}'.format(self.course)

	def to_dict(self):
		data = {
			'id' : self.id,
			'Course': self.course,
			'institution': self.institution,
			'Year':self.year,
			'Percentage' : self.percentage,
			'subjects': self.subjects,
			'user_id':self.user_id
		}
		return data


class Qualifications(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	course = db.Column(db.String(120))
	year = db.Column(db.Integer())
	percentage = db.Column(db.Float())
	subjects = db.Column(db.Text())
	college = db.Column(db.Text())
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Qualification_details: Course {}'.format(self.course)

	def to_dict(self):
		data = {
			'id' : self.id,
			'Course': self.course,
			'Year':self.year,
			'Percentage' : self.percentage,
			'subjects': self.subjects,
			'college': self.college,
			'user_id':self.user_id
		}
		return data


class Certifications(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	course_name = db.Column(db.String(120))
	organization = db.Column(db.String(120))
	credentials = db.Column(db.Text())
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Certification_details: Course Name {} '.format(self.course_name)

	def to_dict(self):
		data = {
			'id' : self.id,
			'course_name': self.course_name,
			'organization':self.organization,
			'credentials' : self.credentials,
			'user_id':self.user_id
		}
		return data

class Projects(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	project_Name = db.Column(db.String(120))
	year = db.Column(db.Integer())
	project_details = db.Column(db.Text())
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Projects : Project Name {} '.format(self.project_name)

	def to_dict(self):
		data = {
			'id' : self.id,
			'project_Name': self.project_Name,
			'year':self.year,
			'project_details' : self.project_details,
			'user_id':self.user_id
		}
		return data

class Experience(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	organization_name = db.Column(db.String(120))
	duration_in_months = db.Column(db.Integer())
	position = db.Column(db.String(120))
	details = db.Column(db.String(500))
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Experience_details : Organization Name {} '.format(self.organization_name)

	def to_dict(self):
		data = {
			'id' : self.id,
			'organization_name': self.organization_name,
			'duration_in_months':self.duration_in_months,
			'position' : self.position,
			'details': self.details,
			'user_id':self.user_id
		}
		return data

class Other_details(db.Model):
	__tablename__ = 'other_details'
	id = db.Column(db.Integer,primary_key=True)
	details = db.Column(db.Text(500))
	profile = db.Column(db.String(500))
	skills = db.Column(db.String(500))
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Other Details {}'.format(self.details)

	def to_dict(self):
		data = {
			'id' : self.id,
			'details': self.details,
			'profile': self.profile,
			'skills': self.skills,
			'user_id':self.user_id
		}
		return data
