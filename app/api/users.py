from app.model import (User, Resume, JD, Demographic_details, Contact_details, Highest_qualification,
					   Qualifications, Certifications, Projects,
					   Experience, Other_details)
from flask_jwt_extended import create_access_token, jwt_required
from flask_jwt_extended import get_jwt_identity, get_raw_jwt
import datetime
from app import jwt, db, app, blacklist
from flask import request, jsonify
from app.api import bp
import re

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
	jti = decrypted_token['jti']
	return jti in blacklist

@bp.route('/api/signup', methods=['POST'])
def signup():
	users = User.query.all()
	json_data = request.get_json()
	new_user = User(username=json_data['username'], email=json_data['email'], recruiter=json_data['recruiter'])
	new_user.set_password(json_data['password'])
	pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
	matches = pattern.findall(new_user.email)
	if not matches:
		return jsonify({'msg':'Please enter a valid email address'}), 400


	for user in users:
		if user.username == new_user.username:
			return jsonify({'msg': 'Username already Exists'}), 400

		if user.email == new_user.email:
			return jsonify({'msg': 'Email already Exists'}), 400

	db.session.add(new_user)
	db.session.commit()

	return jsonify({'msg': 'You have successfully signed up'})


@bp.route('/api/login',methods=['POST'])
def login():
	json_data = request.get_json()
	username = json_data['username']
	password = json_data['password']
	user = User.query.filter_by(username=username).first()

	if user is None:
		return jsonify({'msg':'No user found'}), 404

	elif not user.check_password(password):
		return jsonify({'msg':'Wrong Username or password'}), 404

	expires_delta = datetime.timedelta(days=5)
	token = create_access_token(identity=str(user.id),
									expires_delta=expires_delta)
	return jsonify({'access_token': token})


@bp.route('/api/users', methods = ['GET'])
@jwt_required
def get_all_users():
	users = User.query.all()
	output= []

	if not users:
		return jsonify({'msg':'No Users found'}), 404
	for user in users:
		output.append(user.to_dict())
	return jsonify({'users':output})


@bp.route('/api/resumes', methods = ['GET'])
@jwt_required
def get_all_resumes():
	resumes = Resume.query.all()
	output= []

	if not resumes:
		return jsonify({'msg':'No Resumes found'}), 404
	for resume in resumes:
		output.append(resume.to_dict())
	return jsonify({'resumes':output})


@bp.route('/api/user/<int:user_id>', methods=['GET'])
@jwt_required
def get_one_user(user_id):
	user = User.query.filter_by(id = user_id).first()
	if not user:
		return jsonify({'msg':'User not found'})
	user_data = user.to_dict()

	return jsonify({'user':user_data})


@bp.route('/api/user',methods=['PUT'])
@jwt_required
def update_user():
	users = User.query.all()
	user = User.query.filter_by(id=get_jwt_identity()).first()

	for user_exists in users:
		if user!=user_exists:
			if request.json['username'] == user_exists.username:
				return jsonify({'msg': 'Username already exists'})
	user.username = request.json['username']

	db.session.commit()

	return jsonify({'msg': 'User has been updated'})


@bp.route('/api/user', methods=['DELETE'])
@jwt_required
def delete_user():
	user = User.query.filter_by(id=get_jwt_identity()).first()
	db.session.delete()
	db.session.commit()

	return jsonify({'msg': 'User has bees successfully deleted'})


# Add Resume
@bp.route('/api/user/resume', methods=['POST'])
@jwt_required
def add_resume_path():
	user = User.query.filter_by(id=get_jwt_identity()).first()
	path = request.json['path']
	graph = request.json['graph']
	wcloudname = request.json['wcloudname']
	filename = request.json['filename']
	position = request.json['position']
	resume = Resume(path=path, graph=graph, wcloudname=wcloudname, filename=filename, position=position, user_id=user.id)
	db.session.add(resume)
	db.session.commit()

	return jsonify({'msg': 'Resume has been added'})


# Get Resume
@bp.route('/api/user/<int:user_id>/resume', methods=['GET'])
@jwt_required
def get_resume_path_of_user(user_id):
	user = User.query.filter_by(id=user_id).first()
	if not user:
		return jsonify({'msg':'No user found'}), 404
	details = user.Resume.all()
	if not details:
		return jsonify({'msg':'No details found'}), 404
	output = []

	for detail in details:
		output.append(detail.to_dict())

	return jsonify(({'resumes': output}))


# Delete Resume
@bp.route('/api/user/resume/<int:detail_id>', methods=['DELETE'])
@jwt_required
def delete_resume(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	resume = Resume.query.filter_by(id=detail_id, user_id = user.id).first()

	if not resume:
		return jsonify({'msg':'No details found'}), 404

	db.session.delete(resume)
	db.session.commit()

	return jsonify({'msg':'Details deleted'})


# Add JDs
@bp.route('/api/user/jd', methods = ['POST'])
@jwt_required
def add_jd():
    user = User.query.filter_by(id=get_jwt_identity()).first()
    details = request.json['details']
    position = request.json['position']
    jd = JD(details=details, position=position, user_id=user.id)
    db.session.add(jd)
    db.session.commit()

    return jsonify({'msg': 'Job Description has been added'})

# Get JDs
@bp.route('/api/user/<int:user_id>/jd', methods=['GET'])
@jwt_required
def get_jd_of_user(user_id):
	user = User.query.filter_by(id=user_id).first()
	if not user:
		return jsonify({'msg':'No user found'}), 404
	details = user.JD.all()
	if not details:
		return jsonify({'msg':'No details found'}), 404
	output = []

	for detail in details:
		output.append(detail.to_dict())

	return jsonify(({'jd': output}))

# Update JDs
@bp.route('/api/user/jd/<int:detail_id>', methods = ['PUT'])
@jwt_required
def update_jd(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	jd = JD.query.filter_by(id=detail_id, user_id=user.id).first()
	if not jd:
		return jsonify({'msg':'No details found'}), 404 

	jd.details = request.json['details']
	jd.position = request.json['position']
	db.session.commit()

	return jsonify({'msg': 'JD has been updated'})

# Delete JDs
@bp.route('/api/user/jd/<int:detail_id>', methods=['DELETE'])
@jwt_required
def delete_jd(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	jd = JD.query.filter_by(id=detail_id, user_id = user.id).first()

	if not jd:
		return jsonify({'msg':'No details found'}), 404
	
	db.session.delete(jd)
	db.session.commit()

	return jsonify({'msg':'Details deleted'})


@bp.route('/api/user/demographic_details', methods = ['POST'])
@jwt_required
def add_demographic_details():
	user = User.query.filter_by(id=get_jwt_identity()).first()
	first_name = request.json['first_name']
	last_name = request.json['last_name']
	position = request.json['position']
	dob = request.json['dob']
	nationality = request.json['nationality']
	gender = request.json['gender']
	demographic_details = Demographic_details(first_name=first_name, last_name=last_name, position=position, dob=dob, nationality=nationality, gender=gender, user_id=user.id)
	db.session.add(demographic_details)
	db.session.commit()

	return jsonify({'msg': 'Demographic details has been added'})

@bp.route('/api/user/demographic_details/<int:detail_id>', methods = ['PUT'])
@jwt_required
def update_demographic_details(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	demographic_details = Demographic_details.query.filter_by(id=detail_id, user_id=user.id).first()
	if not demographic_details:
		return jsonif({'msg':'No details found'}), 404 

	demographic_details.first_name = request.json['first_name']
	demographic_details.last_name = request.json['last_name']
	demographic_details.position = request.json['position']
	demographic_details.dob = request.json['dob']
	demographic_details.nationality = request.json['nationality']
	demographic_details.gender = request.json['gender']
	db.session.commit()

	return jsonify({'msg': 'details has been updated'})

@bp.route('/api/user/<int:user_id>/demographic_details', methods=['GET'])
@jwt_required
def get_demographic_details_of_user(user_id):
	user = User.query.filter_by(id=user_id).first()
	if not user:
		return jsonify({'msg':'No user found'}), 404
	details = user.Demographic_details.all()
	if not details:
		return jsonify({'msg':'No details found'}), 404
	output = []

	for detail in details:
		output.append(detail.to_dict())

	return jsonify(({'demographic_details': output}))

@bp.route('/api/user/demographic_details/<int:detail_id>', methods=['DELETE'])
@jwt_required
def delete_demographic_details(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	demographic_details = Demographic_details.query.filter_by(id=detail_id, user_id = user.id).first()

	if not demographic_details:
		return jsonify({'msg':'No details found'}), 404
	
	db.session.delete(demographic_details)
	db.session.commit()

	return jsonify({'msg':'Details deleted'})



@bp.route('/api/user/contact_details', methods=['POST'])
@jwt_required
def add_contact_details():
	user = User.query.filter_by(id=get_jwt_identity()).first()
	email = request.json['email']
	phone_no = request.json['phone_no']
	linkedin_prof = request.json['linkedin_prof']
	address = request.json['address']
	contact_details = Contact_details(email=email, phone_no=phone_no, linkedin_prof=linkedin_prof, address=address, user_id=user.id)
	db.session.add(contact_details)
	db.session.commit()

	return jsonify({'msg':'Contact details has been added'})

@bp.route('/api/user/contact_details/<int:detail_id>', methods=['PUT'])
@jwt_required
def update_contact_details(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	contact_details = Contact_details.query.filter_by(id=detail_id, user_id=user.id).first()
	if not contact_details:
		return jsonify({'msg':'No details found'}), 404

	contact_details.email = request.json['email']
	contact_details.phone_no = request.json['phone_no']
	contact_details.linkedin_prof = request.json['linkedin_prof']
	contact_details.address = request.json['address']
	db.session.commit()

	return jsonify({'msg':'Contact details has been updated'})

@bp.route('/api/user/<int:user_id>/contact_details', methods=['GET'])
@jwt_required
def get_contact_details_of_user(user_id):
	user = User.query.filter_by(id=user_id).first()
	if not user:
		return jsonify({'msg':'No user found'}), 404
	details = user.Contact_details.all()
	if not details:
		return jsonify({'msg':'No details found'}), 404 
	output = []

	for detail in details:
		output.append(detail.to_dict())

	return jsonify(({'contact_details': output}))
 
@bp.route('/api/user/contact_details/<int:detail_id>', methods=['DELETE'])
@jwt_required
def delete_contact_details(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	contact_details = Contact_details.query.filter_by(id=detail_id, user_id = user.id).first()

	if not contact_details:
		return jsonify({'msg':'No details found'}), 404
	
	db.session.delete(contact_details)
	db.session.commit()

	return jsonify({'msg':'Details deleted'})


@bp.route('/api/user/highest_qualification', methods=['POST'])
@jwt_required
def add_highest_qualification():
	user = User.query.filter_by(id=get_jwt_identity()).first()
	course = request.json['course']
	institution = request.json['institution']
	year = request.json['year']
	percentage = request.json['percentage']
	subjects = request.json['subjects']
	highest_qualification = Highest_qualification(course=course, institution=institution, year=year, percentage=percentage, subjects=subjects, user_id=user.id)
	db.session.add(highest_qualification)
	db.session.commit()

	return jsonify({'msg':'Highest Qualification has been added'})

@bp.route('/api/user/highest_qualification/<int:detail_id>', methods=['PUT'])
@jwt_required
def update_highest_qualification(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	highest_qualification = Highest_qualification.query.filter_by(id=detail_id, user_id=user.id).first()
	if not highest_qualification:
		return jsonify({'msg':'No details found'}), 404

	highest_qualification.course = request.json['course']
	highest_qualification.institution = request.json['institution']
	highest_qualification.year = request.json['year']
	highest_qualification.percentage = request.json['percentage']
	highest_qualification.subjects = request.json['subjects']
	db.session.commit()

	return jsonify({'msg':'Highest Qualification has been updated'})

@bp.route('/api/user/<int:user_id>/highest_qualification', methods=['GET'])
@jwt_required
def get_highest_qualification_of_user(user_id):
	user = User.query.filter_by(id=user_id).first()
	if not user:
		return jsonify({'msg':'No user found'}), 404
	details = user.highest_qualification.all()
	if not details:
		return jsonify({'msg':'No details found'}), 404
	output = []

	for detail in details:
		output.append(detail.to_dict())

	return jsonify(({'highest_qualification': output}))
 
@bp.route('/api/user/highest_qualification/<int:detail_id>', methods=['DELETE'])
@jwt_required
def delete_highest_qualification(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	highest_qualification = Highest_qualification.query.filter_by(id=detail_id, user_id = user.id).first()

	if not highest_qualification:
		return jsonify({'msg':'No details found'}), 404
	
	db.session.delete(highest_qualification)
	db.session.commit()

	return jsonify({'msg':'Details deleted'})

@bp.route('/api/user/qualification', methods=['POST'])
@jwt_required
def add_qualification():
	user = User.query.filter_by(id=get_jwt_identity()).first()
	course = request.json['course']
	year = request.json['year']
	percentage = request.json['percentage']
	subjects = request.json['subjects']
	college = request.json['college']
	qualification = Qualifications(course=course, year=year, percentage=percentage, subjects=subjects, college=college, user_id=user.id)
	db.session.add(qualification)
	db.session.commit()

	return jsonify({'msg':'Qualification has been added'})

@bp.route('/api/user/qualification/<int:detail_id>', methods=['PUT'])
@jwt_required
def update_qualification(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	qualification = Qualifications.query.filter_by(id=detail_id, user_id=user.id).first()
	if not qualification:
		return jsonify({'msg':'No details found'}), 404

	qualification.course = request.json['course']
	qualification.year = request.json['year']
	qualification.percentage = request.json['percentage']
	qualification.subjects = request.json['subjects']
	qualification.college = request.json['college']
	db.session.commit()

	return jsonify({'msg':'Qualification has been updated'})

@bp.route('/api/user/<int:user_id>/qualification', methods=['GET'])
@jwt_required
def get_qualification_of_user(user_id):
	user = User.query.filter_by(id=user_id).first()
	if not user:
		return jsonify({'msg':'No user found'}), 404
	details = user.Qualifications.all()
	if not details:
		return jsonify({'msg':'No details found'}), 404
	output = []

	for detail in details:
		output.append(detail.to_dict())

	return jsonify(({'qualification': output}))
 
@bp.route('/api/user/qualification/<int:detail_id>', methods=['DELETE'])
@jwt_required
def delete_qualification(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	qualification = Qualifications.query.filter_by(id=detail_id, user_id = user.id).first()

	if not qualification:
		return jsonify({'msg':'No details found'}), 404
	
	db.session.delete(qualification)
	db.session.commit()

	return jsonify({'msg':'Details deleted'})

@bp.route('/api/user/certification', methods=['POST'])
@jwt_required
def add_certification():
	user = User.query.filter_by(id=get_jwt_identity()).first()
	course_name = request.json['course_name']
	organization = request.json['organization']
	credentials = request.json['credentials']
	certification = Certifications(course_name=course_name, organization=organization, credentials=credentials, user_id=user.id)
	db.session.add(certification)
	db.session.commit()

	return jsonify({'msg':'Certification has been added'})

@bp.route('/api/user/certification/<int:detail_id>', methods=['PUT'])
@jwt_required
def update_certification(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	certification = Certifications.query.filter_by(id=detail_id, user_id=user.id).first()
	if not certification:
		return jsonify({'msg':'No details found'}), 404

	certification.course_name = request.json['course_name']
	certification.organization = request.json['organization']
	certification.credentials = request.json['credentials']
	db.session.commit()

	return jsonify({'msg':'Certification has been updated'})


@bp.route('/api/user/<int:user_id>/certification', methods=['GET'])
@jwt_required
def get_certification_of_user(user_id):
	user = User.query.filter_by(id=user_id).first()
	if not user:
		return jsonify({'msg':'No user found'}), 404
	details = user.Certifications.all()
	if not details:
		return jsonify({'msg':'No details found'}), 404
	output = []

	for detail in details:
		output.append(detail.to_dict())

	return jsonify(({'certifications': output}))
 
@bp.route('/api/user/certification/<int:detail_id>', methods=['DELETE'])
@jwt_required
def delete_certification(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	certification = Certifications.query.filter_by(id=detail_id, user_id = user.id).first()

	if not certification:
		return jsonify({'msg':'No details found'}), 404
	
	db.session.delete(certification)
	db.session.commit()

	return jsonify({'msg':'Details deleted'})
  

@bp.route('/api/user/project', methods=['POST'])
@jwt_required
def add_project():
	user = User.query.filter_by(id=get_jwt_identity()).first()
	project_Name = request.json['project_Name']
	year = request.json['year']
	project_details = request.json['project_details']
	project = Projects(project_Name=project_Name, year=year, project_details=project_details, user_id=user.id)
	db.session.add(project)
	db.session.commit()

	return jsonify({'msg': 'Project has been added'})

@bp.route('/api/user/project/<int:detail_id>', methods=['PUT'])
@jwt_required
def update_project(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	project = Projects.query.filter_by(id=detail_id, user_id=user.id).first()
	if not project:
		return jsonify({'msg':'No details found'}), 404

	project.project_Name = request.json['project_Name']
	project.year = request.json['year']
	project.project_details = request.json['project_details']
	db.session.commit()

	return jsonify({'msg': 'Project has been updated'})

@bp.route('/api/user/<int:user_id>/project', methods=['GET'])
@jwt_required
def get_project_details_of_user(user_id):
	user = User.query.filter_by(id=user_id).first()
	if not user:
		return jsonify({'msg':'No user found'}), 404
	details = user.Projects.all()
	if not details:
		return jsonify({'msg':'No details found'}), 404 
	output = []

	for detail in details:
		output.append(detail.to_dict())

	return jsonify(({'projects': output}))

@bp.route('/api/user/project/<int:detail_id>', methods=['DELETE'])
@jwt_required
def delete_project(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	project = Projects.query.filter_by(id=detail_id, user_id = user.id).first()

	if not project:
		return jsonify({'msg':'No details found'}), 404
	
	db.session.delete(project)
	db.session.commit()

	return jsonify({'msg':'Details deleted'})
  

@bp.route('/api/user/experience', methods=['POST'])
@jwt_required
def add_experience():
	user = User.query.filter_by(id=get_jwt_identity()).first()
	organization_name = request.json['organization_name']
	duration_in_months = request.json['duration_in_months']
	position = request.json['position']
	details = request.json['details']
	experience = Experience(organization_name=organization_name, duration_in_months=duration_in_months, position=position, details=details, user_id=user.id)
	db.session.add(experience)
	db.session.commit()

	return jsonify({'msg':'Experience has been added'})

@bp.route('/api/user/experience/<int:detail_id>', methods=['PUT'])
@jwt_required
def update_experience(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	experience = Experience.query.filter_by(id=detail_id, user_id=user.id).first()
	if not experience:
		return jsonify({'msg':'No details found'}), 404

	experience.organization_name = request.json['organization_name']
	experience.duration_in_months = request.json['duration_in_months']
	experience.position = request.json['position']
	experience.details = request.json['details']
	db.session.commit()

	return jsonify({'msg':'Experience has been updated'})

@bp.route('/api/user/<int:user_id>/experience', methods=['GET'])
@jwt_required
def get_experience_details_of_user(user_id):
	user = User.query.filter_by(id=user_id).first()
	if not user:
		return jsonify({'msg':'No user found'}), 404
	details = user.Experience.all()
	if not details:
		return jsonify({'msg':'No details found'}), 404
	output = []

	for detail in details:
		output.append(detail.to_dict())

	return jsonify(({'Experience': output}))

@bp.route('/api/user/experience/<int:detail_id>', methods=['DELETE'])
@jwt_required
def delete_experience(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	experience = Experience.query.filter_by(id=detail_id, user_id = user.id).first()

	if not experience:
		return jsonify({'msg':'No details found'}), 404
	
	db.session.delete(experience)
	db.session.commit()

	return jsonify({'msg':'Details deleted'})
 

@bp.route('/api/user/other_details', methods=['POST'])
@jwt_required
def add_other_details():
	user = User.query.filter_by(id=get_jwt_identity()).first()
	details = request.json['details']
	profile = request.json['profile']
	skills = request.json['skills']
	other_details = Other_details(details=details, profile=profile, skills=skills, user_id=user.id)
	db.session.add(other_details)
	db.session.commit()

	return jsonify({'msg':'Other details has been added'})

@bp.route('/api/user/other_details/<int:detail_id>', methods=['PUT'])
@jwt_required
def update_other_details(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	other_details = Other_details.query.filter_by(id=detail_id, user_id=user.id).first()
	if not other_details:
		return jsonify({'msg':'No details found'}), 404

	other_details.details = request.json['details']
	other_details.skills = request.json['skills']
	other_details.profile = request.json['profile']
	db.session.commit()

	return jsonify({'msg':'Other details has been updated'})

@bp.route('/api/user/<int:user_id>/other_details', methods=['GET'])
@jwt_required
def get_other_details_of_user(user_id):
	user = User.query.filter_by(id=user_id).first()
	if not user:
		return jsonify({'msg':'No user found'}), 404
	details = user.Other_details.all()
	if not details:
		return jsonify({'msg':'No details found'}), 404
	output = []

	for detail in details:
		output.append(detail.to_dict())

	return jsonify(({'other_details': output}))

@bp.route('/api/user/other_details/<int:detail_id>', methods=['DELETE'])
@jwt_required
def delete_other_details(detail_id):
	user = User.query.filter_by(id=get_jwt_identity()).first()
	other_details = Other_details.query.filter_by(id=detail_id, user_id = user.id).first()

	if not other_details:
		return jsonify({'msg':'No details found'}), 404
	
	db.session.delete(other_details)
	db.session.commit()

	return jsonify({'msg':'Details deleted'})

@bp.route('/api/logout', methods=['DELETE'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200