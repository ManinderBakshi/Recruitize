from app import db
from flask import Flask, render_template, redirect, flash, url_for, request, send_file, send_from_directory
from flask import current_app, g
from app.main.forms import (EditProfileForm, demographic_form, contact_form,
                            highest_qualification_form, qualification_form,
                            certification_form, project_form, experience_form,
                            other_details_forms)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app.model import (User, Demographic_details, Contact_details,
                       Highest_qualification, Qualifications,
                       Certifications, Projects, Experience, Other_details)
from datetime import datetime
from app.main import bp
import requests
import os
import pdfkit
from app.auth.routes import session, host
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from matplotlib import pyplot as plt
from matplotlib import pyplot as plts
from tika import parser
import io
import re
import nltk
import json
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
import tabula
from tika import parser
from nltk.corpus import stopwords 
import docx2txt
from geopy.geocoders import Nominatim
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
import operator
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer
import sklearn
import pickle
from sklearn.feature_extraction.text import CountVectorizer
import plotly.express as px
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer as countVectorizer 

from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, login_required, logout_user
from app.model import User
from werkzeug.urls import url_parse


import mammoth
import re
import io
import nltk
import json
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
import tabula
from tika import parser
from spacy.matcher import Matcher
from nltk.corpus import stopwords 
import spacy
from geopy.geocoders import Nominatim
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer
import sklearn
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from matplotlib import pyplot as plt
import numpy as np
from PIL import Image
from datetime import date 
import datetime

import operator
import itertools
from bs4 import BeautifulSoup
from pdf2docx.main import parse
import matplotlib as mp
import pickle
import plotly.express as px


app = Flask(__name__)
app.config["UPLOADED_RESUMES"] = os.getcwd()+"//Uploaded_Resumes"
app.config["CREATED_RESUMES"] = os.getcwd()+"//Created_Resumes"
app.config["CREATED_REPORTS"] = os.getcwd()+"//Created_Reports"
app.config["CREATED_WORDCLOUDS"] = os.getcwd()+"//app//static//img//Created_WordClouds"
app.config["CREATED_GRAPHS"] = os.getcwd()+"//app//static//img//Created_Graphs"
app.config["CREATED_PIE"] = os.getcwd()+"//app//static//img//Created_Pie"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["PDF", "DOC", "DOCX"]

# Website Index page
@bp.route('/', methods=['GET','POST'])
@bp.route('/index', methods=['GET','POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    username = form.username.data
    password = form.password.data

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        login_response = requests.post('{0}/api/login'.format(host), json={
            "username": username, "password": password})

        if login_response.status_code == 404:
            login_resp_dict = login_response.json()
            flash(login_resp_dict.get('msg'))
            return redirect(url_for('main.index'))
        session['api_token'] = login_response.json().get('access_token')

        if user is None or not user.check_password(password):
            login_resp_dict = login_response.json()
            flash(login_resp_dict.get('msg'))
            return redirect(url_for('main.index'))

        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':
            if user.recruiter == True:
                login_user(user)
                next_page = url_for('main.index')

            elif user.recruiter == False:
                login_user(user)
                next_page = url_for('main.index')

        return redirect(next_page)
    return render_template('index.html', form=form)

# Website Home Page
@bp.route('/home', methods=['GET', 'POST'])
@login_required 
def home():
    user_id = current_user.id
    return render_template('home.html', user_id=user_id)


# Resume Builder

@bp.route('/resume_builder', methods=['GET', 'POST'])
@login_required 
def resume_builder():
    user_id = current_user.id

    # Demographic details
    demog_json = {}
    demog_list = {}
    demog_resp = requests.get('{0}/api/user/{1}/demographic_details'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if demog_resp.status_code == 200:
        demog_json = demog_resp.json()
        demog_list = demog_json['demographic_details']

    # Contact Details
    contact_json = {}
    contact_list = {}
    contact_resp = requests.get('{0}/api/user/{1}/contact_details'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if contact_resp.status_code == 200:
        contact_json = contact_resp.json()
        contact_list = contact_json['contact_details']
    
    # Highest qualification Details
    hqual_json = {}
    hqual_list = {}
    hqual_resp = requests.get('{0}/api/user/{1}/highest_qualification'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if hqual_resp.status_code == 200:
        hqual_json = hqual_resp.json()
        hqual_list = hqual_json['highest_qualification']
    
    # Qualification Details
    qual_json = {}
    qual_list = {}
    qual_resp = requests.get('{0}/api/user/{1}/qualification'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if qual_resp.status_code == 200:
        qual_json = qual_resp.json()
        qual_list = qual_json['qualification']
    
    # Certification Details
    cert_json = {}
    cert_list = {}
    cert_resp = requests.get('{0}/api/user/{1}/certification'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if cert_resp.status_code == 200:
        cert_json = cert_resp.json()
        cert_list = cert_json['certifications']
    
    # Projects Details
    pro_json = {}
    pro_list = {}
    pro_resp = requests.get('{0}/api/user/{1}/project'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if pro_resp.status_code == 200:
        pro_json = pro_resp.json()
        pro_list = pro_json['projects']
    
    # Experience Details
    exp_json = {}
    exp_list = {}
    exp_resp = requests.get('{0}/api/user/{1}/experience'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if exp_resp.status_code == 200:
        exp_json = exp_resp.json()
        exp_list = exp_json['Experience']
    
     # Other Details
    oth_json = {}
    oth_list = {}
    oth_resp = requests.get('{0}/api/user/{1}/other_details'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if oth_resp.status_code == 200:
        oth_json = oth_resp.json()
        oth_list = oth_json['other_details']

    
    return render_template("resume_builder.html", title='Resume Builder', user_id=user_id, demog_list=demog_list, contact_list=contact_list, hqual_list=hqual_list, qual_list=qual_list, cert_list=cert_list, pro_list=pro_list, exp_list=exp_list, oth_list=oth_list)




@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)

    if form.validate_on_submit():
        current_user.username = form.username.data

        response_user_put = requests.put(
         '{0}/api/user'.format(host),
         json={"username": form.username.data},
         headers={'Authorization': 'Bearer {}'.format(session['api_token'])})

        if response_user_put.status_code == 200 or 400:
            flash(response_user_put.json()['msg'])
            return redirect(url_for('main.student'))

        return redirect(url_for('main.edit_profile'))
    
    return render_template('profile.html', form=form)




# Adding Resume

def allowed_file(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

@bp.route('/user/add_resume', methods=['POST', 'GET'])
@login_required
def add_resume():
    if request.method == "POST":

        if request.files:

            doc = request.files["doc"]
            position = request.form.get('position')
            git = request.form.get('github')
            
            if doc.filename == "":
                print("No Filename")
                return redirect(url_for('main.add_resume'))
            if allowed_file(doc.filename):
                filename = secure_filename(doc.filename)
                wcloudname = filename.rsplit(".", 1)[0]  + '.png'
                graph = filename.rsplit(".", 1)[0]  + '.png'
                git = os.path.join(git, '?tab=repositories')
                path = os.path.join(app.config["UPLOADED_RESUMES"], filename)
  
                add_resume_resp = requests.post('{0}/api/user/resume'.format(host), json={"path": path, "graph":graph, "wcloudname":wcloudname, "filename": filename, "position":position, "git":git,},
                headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
                
                if add_resume_resp.status_code == 200:
                    doc.save(path)
                   
                    return redirect(url_for('main.show_resumes'))
                    
            else:
                print("That file extension is not allowed")
                return redirect(url_for('main.add_resume'))

    return render_template("upload_resume.html")


# Showing Resumes
@bp.route('/user/resume', methods=['POST', 'GET'])
@login_required
def show_resumes():
    user_id = current_user.id

    resume_json = {}
    resume_list = {}
    resume_resp = requests.get('{0}/api/user/{1}/resume'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if resume_resp.status_code == 200:
        resume_json = resume_resp.json()
        resume_list = resume_json['resumes']

    return render_template("show_resumes.html", title='Show Resumes', user_id=user_id, resume_list=resume_list)


import  requests
from bs4 import BeautifulSoup

def repositories(URL):
    repo_lists=[]
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    repos = soup.findAll('li', itemprop="owns")
    for repo in repos:
        r={}
        title_repo = repo.find('a', itemprop="name codeRepository")
        lang = repo.find('span', itemprop="programmingLanguage")
        status = repo.find('relative-time', class_="no-wrap")
        repo_url = ("".join(["https://github.com/",title_repo['href']]))
        repo_page = requests.get(repo_url)
        new_soup = BeautifulSoup(repo_page.content, 'html.parser')
        commits_head = new_soup.find('span', class_="d-none d-sm-inline")
        readme_head = new_soup.find('div', class_="Box-body px-5 pb-5")
        if(title_repo.text):
            r["title"] = title_repo.text
        if(lang):
            r['languages'] = lang.text
        if(status):
           r['status'] = status.text
        if(commits_head):
            commits = commits_head.find('strong')
            r['commits'] = commits.text
        
        repo_lists.append(r)
    
    return repo_lists

# Analyze Resumes
@bp.route('/user/scan_resume/<filename>', methods=['GET', 'POST'])
@login_required
def scan_resume(filename):
    path = os.path.join(app.config["UPLOADED_RESUMES"], filename)
    data = create_user_json(filename,path)

    resume_json = {}
    resume_list = {}
    resume_resp = requests.get('{0}/api/user/resume/{1}'.format(host, filename), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if resume_resp.status_code == 200:
        resume_json = resume_resp.json()
        resume_list = resume_json['resumes']
    
    
    
    return render_template("analyze_resume.html", title='Analysis', data=data)


# Report Generation
@bp.route('/user/report/<filename>', methods=['GET', 'POST'])
@login_required
def report(filename):

    return send_from_directory(app.config["CREATED_REPORTS"],
                               filename)




# View Resume
@bp.route('/Word_cloud/<filename>')
def created_wordcloud(filename):
    return send_from_directory(app.config['CREATED_RESUMES'],
                               filename)


# Delete Resume
@bp.route('/user/delete_resume/<int:resume_id>')
@login_required
def delete_resume(resume_id):
    del_resume_resp = requests.delete('{0}/api/user/resume/{1}'.format(host, resume_id),
                                     headers={'Authorization': 'Bearer {}'.format(session['api_token'])})

    if del_resume_resp.status_code == 200 or 400 or 401 or 404:
        flash(del_resume_resp.json()['msg'])
        return redirect(url_for('main.show_resumes'))


# View Resume
@bp.route('/Resumes/<filename>')
def uploaded_resume(filename):
    return send_from_directory(app.config['UPLOADED_RESUMES'],
                               filename)


# Adding Job Descriptions
@bp.route('/user/add_jd', methods=['POST', 'GET'])
@login_required
def add_jd():
    if request.method == "POST":
        details = request.form.get('details')
        position = request.form.get('position')

        add_jd_resp = requests.post('{0}/api/user/jd'.format(host), json={"details": details, "position":position},
                headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
        if add_jd_resp.status_code==200:
            return redirect(url_for('main.recruiter'))

    return render_template("add_jd.html")


# Showing JDs
@bp.route('/user/jd', methods=['POST', 'GET'])
@login_required
def show_jd():
    user_id = current_user.id

    jd_json = {}
    jd_list = {}
    jd_resp = requests.get('{0}/api/user/{1}/jd'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if jd_resp.status_code == 200:
        jd_json = jd_resp.json()
        jd_list = jd_json['jd']

    return render_template("show_jd.html", title='Show JDs', user_id=user_id, jd_list=jd_list)


# Delete JD
@bp.route('/user/delete_jd/<int:jd_id>')
@login_required
def delete_jd(jd_id):
    del_jd_resp = requests.delete('{0}/api/user/jd/{1}'.format(host, jd_id),
                                     headers={'Authorization': 'Bearer {}'.format(session['api_token'])})

    if del_jd_resp.status_code == 200 or 400 or 401 or 404:
        flash(del_jd_resp.json()['msg'])
        return redirect(url_for('main.show_jd'))


# Matching JDs

@bp.route('/user/match_jd/<jd_position>/<jd_details>')
@login_required
def match_jd(jd_position, jd_details):
    matchings = []
    resume_json = {}
    resume_list = {}
    resume_resp = requests.get('{0}/api/resumes'.format(host), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if resume_resp.status_code == 200:
        resume_json = resume_resp.json()
        resume_list = resume_json['resumes']
        
    
    for resume in resume_list:
        if resume['position'] == jd_position:
            resume_path = resume['path']
            filename = resume['filename']
        
            cv_txt = resume_text_from_pdf(resume_path)
            
            skills = extract_skills(cv_txt)
            
            score = similarity_percentage(skills,jd_details)
            match = {'path':resume_path, 'score':score, 'filename':filename}
            matchings.append(match)

    return render_template('matchings.html', matchings=matchings)
            
            
            
            


# Adding demographic details
@bp.route('/user/add_demographic_details', methods=['POST', 'GET'])
@login_required
def add_demographic_details():
    form = demographic_form()

    first_name = form.first_name.data
    last_name = form.last_name.data
    position = form.position.data
    dob = request.form.get('dob')
    gender = form.gender.data
    nationality = form.nationality.data

    if form.validate_on_submit():
        add_demog_response = requests.post('{0}/api/user/demographic_details'.format(host), json={
            "first_name": first_name, "last_name": last_name, "position":position, "dob":dob, "gender":gender, "nationality":nationality},
            headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
        flash(add_demog_response.json()['msg'])
        return redirect(url_for('main.resume_builder'))

    return render_template('demog.html', title='Add Demographic details', form=form)


# Adding Contact details

@bp.route('/user/add_contact_details', methods=['POST', 'GET'])
@login_required
def add_contact_details():
    form = contact_form()

    address = form.address.data
    phone_no = form.phone_no.data
    linkedin_prof = form.linkedin_prof.data
    email = form.email.data

    if form.validate_on_submit():
        add_contact_response = requests.post('{0}/api/user/contact_details'.format(host), json={
            "address": address, "phone_no": phone_no, "linkedin_prof":linkedin_prof, "email":email},
            headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
        flash(add_contact_response.json()['msg'])
        return redirect(url_for('main.resume_builder'))

    return render_template('contact.html', title='Add Contact details', form=form)


# Adding Highest Qualification

@bp.route('/user/add_highest_qualification', methods=['POST', 'GET'])
@login_required
def add_highest_qualification():
    form = highest_qualification_form()

    course = form.course.data
    institution = form.institution.data
    year = form.year.data
    percentage = form.percentage.data
    subjects = form.subjects.data

    if form.validate_on_submit():
        add_hqual_response = requests.post('{0}/api/user/highest_qualification'.format(host), json={
            "course": course, "institution":institution, "year": year, "percentage":percentage, "subjects":subjects},
            headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
        flash(add_hqual_response.json()['msg'])
        return redirect(url_for('main.resume_builder'))

    return render_template('hqual.html', title='Add Highest Qualification', form=form)


# Adding Qualification

@bp.route('/user/add_qualification', methods=['POST', 'GET'])
@login_required
def add_qualification():
    form = qualification_form()

    course = form.course.data
    year = form.year.data
    percentage = form.percentage.data
    subjects = form.subjects.data
    college = form.college.data

    if form.validate_on_submit():
        add_qual_response = requests.post('{0}/api/user/qualification'.format(host), json={
            "course": course, "year": year, "percentage":percentage, "subjects":subjects, "college":college},
            headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
        flash(add_qual_response.json()['msg'])
        return redirect(url_for('main.resume_builder'))

    return render_template('qual.html', title='Add Qualification', form=form)


# Adding certification

@bp.route('/user/add_certification', methods=['POST', 'GET'])
@login_required
def add_certification():
    form = certification_form()

    course = form.course.data
    organization = form.organization.data
    credentials = form.credentials.data

    if form.validate_on_submit():
        add_cert_response = requests.post('{0}/api/user/certification'.format(host), json={
            "course_name": course, "organization": organization, "credentials":credentials},
            headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
        flash(add_cert_response.json()['msg'])
        return redirect(url_for('main.resume_builder'))

    return render_template('cert.html', title='Add Certification', form=form)


# Adding Project

@bp.route('/user/add_project', methods=['POST', 'GET'])
@login_required
def add_project():
    form = project_form()

    project_Name = form.project_Name.data
    project_details = form.project_details.data
    year = form.year.data

    if form.validate_on_submit():
        add_pro_response = requests.post('{0}/api/user/project'.format(host), json={
            "project_Name": project_Name, "project_details": project_details, "year":year},
            headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
        flash(add_pro_response.json()['msg'])
        return redirect(url_for('main.resume_builder'))

    return render_template('proj.html', title='Add Project', form=form)


# Adding Experience

@bp.route('/user/add_experience', methods=['POST', 'GET'])
@login_required
def add_experience():
    form = experience_form()

    organization_name = form.organization_name.data
    position = form.position.data
    duration_in_months = form.duration_in_months.data
    details = form.details.data

    if form.validate_on_submit():
        add_exp_response = requests.post('{0}/api/user/experience'.format(host), json={
            "organization_name": organization_name, "position": position, "duration_in_months":duration_in_months, "details":details},
            headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
        flash(add_exp_response.json()['msg'])
        return redirect(url_for('main.resume_builder'))

    return render_template('exp.html', title='Add Experience', form=form)


# Adding Other details

@bp.route('/user/add_other_details', methods=['POST', 'GET'])
@login_required
def add_other_details():
    form = other_details_forms()

    other_details = form.other_details.data
    profile = form.profile.data 
    skills = form.skills.data

    if form.validate_on_submit():
        add_oth_response = requests.post('{0}/api/user/other_details'.format(host), json={
            "details": other_details, "skills": skills, "profile":profile},
            headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
        flash(add_oth_response.json()['msg'])
        return redirect(url_for('main.resume_builder'))

    return render_template('oth.html', title='Add Other Details', form=form)


# Updating Demographic Details

@bp.route('/user/update_demographic_details/<int:detail_id>', methods=['POST', 'GET'])
@login_required
def update_demographic_details(detail_id):
    form = demographic_form()

    first_name = form.first_name.data
    last_name = form.last_name.data
    position = form.position.data
    dob = form.dob.data
    gender = form.gender.data
    nationality = form.nationality.data

    if form.validate_on_submit():
        update_demog_response = requests.put('{0}/api/user/demographic_details/{1}'.format(host, detail_id), json={
            "first_name": first_name, "last_name": last_name, "position":position, "dob":dob, "gender":gender, "nationality":nationality},
            headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
        flash(update_demog_response.json()['msg'])
        return redirect(url_for('main.resume_builder'))

    return render_template('demog.html', title='Add Demographic details', form=form)


# Updating Contact Details

@bp.route('/user/update_contact_details/<int:detail_id>', methods=['POST', 'GET'])
@login_required
def update_contact_details(detail_id):
    form = contact_form()

    address = form.address.data
    phone_no = form.phone_no.data
    linkedin_prof = form.linkedin_prof.data
    email = form.email.data

    if form.validate_on_submit():
        update_contact_response = requests.put('{0}/api/user/contact_details/{1}'.format(host, detail_id), json={
            "address": address, "phone_no": phone_no, "linkedin_prof":linkedin_prof, "email":email},
            headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
        flash(update_contact_response.json()['msg'])
        return redirect(url_for('main.resume_builder'))

    return render_template('contact.html', title='Add Contact details', form=form)


# Updating Highest Qualification

@bp.route('/user/update_highest_qualification/<int:detail_id>', methods=['POST', 'GET'])
@login_required
def update_highest_qualification(detail_id):
    form = highest_qualification_form()

    course = form.course.data
    institution = form.institution.data
    year = form.year.data
    percentage = form.percentage.data
    subjects = form.subjects.data

    if form.validate_on_submit():
        update_hqual_response = requests.put('{0}/api/user/highest_qualification/{1}'.format(host, detail_id), json={
            "course": course, "institution":institution, "year": year, "percentage":percentage, "subjects":subjects},
            headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
        flash(update_hqual_response.json()['msg'])
        return redirect(url_for('main.resume_builder'))

    return render_template('hqual.html', title='Add Highest Qualification', form=form)


# Updating Qualification

@bp.route('/user/update_qualification/<int:detail_id>', methods=['POST', 'GET'])
@login_required
def update_qualification(detail_id):
    form = qualification_form()

    course = form.course.data
    year = form.year.data
    percentage = form.percentage.data
    subjects = form.subjects.data
    college = form.college.data
    if form.validate_on_submit():
        update_qual_response = requests.put('{0}/api/user/qualification/{1}'.format(host, detail_id), json={
            "course": course, "college":college, "year": year, "percentage":percentage, "subjects":subjects},
            headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
        flash(update_qual_response.json()['msg'])
        return redirect(url_for('main.resume_builder'))

    return render_template('qual.html', title='Update Qualification', form=form)


# Updating Certification

@bp.route('/user/update_certification/<int:detail_id>', methods=['POST', 'GET'])
@login_required
def update_certification(detail_id):
    form = certification_form()

    course = form.course.data
    organization = form.organization.data
    credentials = form.credentials.data

    if form.validate_on_submit():
        update_cert_response = requests.put('{0}/api/user/certification/{1}'.format(host, detail_id), json={
            "course_name": course, "organization": organization, "credentials":credentials},
            headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
        flash(update_cert_response.json()['msg'])
        return redirect(url_for('main.resume_builder'))

    return render_template('cert.html', title='Update Certification', form=form)


# Updating Project

@bp.route('/user/update_project/<int:detail_id>', methods=['POST', 'GET'])
@login_required
def update_project(detail_id):
    form = project_form()

    project_Name = form.project_Name.data
    project_details = form.project_details.data
    year = form.year.data

    if form.validate_on_submit():
        update_pro_response = requests.put('{0}/api/user/project/{1}'.format(host, detail_id), json={
            "project_Name": project_Name, "project_details": project_details, "year":year},
            headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
        flash(update_pro_response.json()['msg'])
        return redirect(url_for('main.resume_builder'))

    return render_template('proj.html', title='Update Project', form=form)


# Updating Experience

@bp.route('/user/update_experience/<int:detail_id>', methods=['POST', 'GET'])
@login_required
def update_experience(detail_id):
    form = experience_form()

    organization_name = form.organization_name.data
    position = form.position.data
    duration_in_months = form.duration_in_months.data
    details = form.details.data

    if form.validate_on_submit():
        update_exp_response = requests.put('{0}/api/user/experience/{1}'.format(host, detail_id), json={
            "organization_name": organization_name, "position": position, "duration_in_months":duration_in_months, "details":details},
            headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
        flash(update_exp_response.json()['msg'])
        return redirect(url_for('main.resume_builder'))

    return render_template('exp.html', title='Update Experience', form=form)


# Updating Other Details

@bp.route('/user/update_other_details/<int:detail_id>', methods=['POST', 'GET'])
@login_required
def update_other_details(detail_id):
    form = other_details_forms()

    other_details = form.other_details.data
    skills = form.skills.data 
    profile = form.profile.data

    if form.validate_on_submit():
        update_oth_response = requests.put('{0}/api/user/other_details/{1}'.format(host, detail_id), json={
            "details": other_details, "profile":profile, "skills":skills},
            headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
        if update_oth_response.status_code == 200:
            resp_dict = update_oth_response.json()
            flash(resp_dict.get('msg'))

            return redirect(url_for('main.resume_builder'))

    return render_template('oth.html', title='Update Other Details', form=form)


# Deleting Demogtaphic Details

@bp.route('/user/delete_demographic_details/<int:detail_id>')
@login_required
def delete_demographic_details(detail_id):
    del_demog_resp = requests.delete('{0}/api/user/demographic_details/{1}'.format(host, detail_id),
                                     headers={'Authorization': 'Bearer {}'.format(session['api_token'])})

    if del_demog_resp.status_code == 200 or 400 or 401 or 404:
        flash(del_demog_resp.json()['msg'])
        return redirect(url_for('main.resume_builder'))


# Deleting Contact Details

@bp.route('/user/delete_contact_details/<int:detail_id>')
@login_required
def delete_contact_details(detail_id):
    del_contact_resp = requests.delete('{0}/api/user/contact_details/{1}'.format(host, detail_id),
                                     headers={'Authorization': 'Bearer {}'.format(session['api_token'])})

    if del_contact_resp.status_code == 200 or 400 or 401 or 404:
        flash(del_contact_resp.json()['msg'])
        return redirect(url_for('main.resume_builder'))

# Deleting Highest Qualification

@bp.route('/user/delete_highest_qualification/<int:detail_id>')
@login_required
def delete_highest_qualification(detail_id):
    del_hqual_resp = requests.delete('{0}/api/user/highest_qualification/{1}'.format(host, detail_id),
                                     headers={'Authorization': 'Bearer {}'.format(session['api_token'])})

    if del_hqual_resp.status_code == 200 or 400 or 401 or 404:
        flash(del_hqual_resp.json()['msg'])
        return redirect(url_for('main.resume_builder'))


# Deleting Qualification

@bp.route('/user/delete_qualification/<int:detail_id>')
@login_required
def delete_qualification(detail_id):
    del_qual_resp = requests.delete('{0}/api/user/qualification/{1}'.format(host, detail_id),
                                     headers={'Authorization': 'Bearer {}'.format(session['api_token'])})

    if del_qual_resp.status_code == 200 or 400 or 401 or 404:
        flash(del_qual_resp.json()['msg'])
        return redirect(url_for('main.resume_builder'))


# Deleting Certification

@bp.route('/user/delete_certification/<int:detail_id>')
@login_required
def delete_certification(detail_id):
    del_cert_resp = requests.delete('{0}/api/user/certification/{1}'.format(host, detail_id),
                                     headers={'Authorization': 'Bearer {}'.format(session['api_token'])})

    if del_cert_resp.status_code == 200 or 400 or 401 or 404:
        flash(del_cert_resp.json()['msg'])
        return redirect(url_for('main.resume_builder'))


# Deleting Project

@bp.route('/user/delete_project/<int:detail_id>')
@login_required
def delete_project(detail_id):
    del_proj_resp = requests.delete('{0}/api/user/project/{1}'.format(host, detail_id),
                                     headers={'Authorization': 'Bearer {}'.format(session['api_token'])})

    if del_proj_resp.status_code == 200 or 400 or 401 or 404:
        flash(del_proj_resp.json()['msg'])
        return redirect(url_for('main.resume_builder'))


# Deleting Experience

@bp.route('/user/delete_experience/<int:detail_id>')
@login_required
def delete_experience(detail_id):
    del_exp_resp = requests.delete('{0}/api/user/experience/{1}'.format(host, detail_id),
                                     headers={'Authorization': 'Bearer {}'.format(session['api_token'])})

    if del_exp_resp.status_code == 200 or 400 or 401 or 404:
        flash(del_exp_resp.json()['msg'])
        return redirect(url_for('main.resume_builder'))


# Deleting Other Details

@bp.route('/user/delete_other_details/<int:detail_id>')
@login_required
def delete_other_details(detail_id):
    del_oth_resp = requests.delete('{0}/api/user/other_details/{1}'.format(host, detail_id),
                                     headers={'Authorization': 'Bearer {}'.format(session['api_token'])})

    if del_oth_resp.status_code == 200 or 400 or 401 or 404:
        flash(del_oth_resp.json()['msg'])
        return redirect(url_for('main.resume_builder'))


@bp.route('/resume', methods=['GET', 'POST'])
@login_required
def resume_user():
    user_id = current_user.id
    user_name = current_user.username

    # Demographic details
    demog_json = {}
    demog_list = {}
    demog_resp = requests.get('{0}/api/user/{1}/demographic_details'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if demog_resp.status_code == 200:
        demog_json = demog_resp.json()
        demog_list = demog_json['demographic_details']

    # Contact Details
    contact_json = {}
    contact_list = {}
    contact_resp = requests.get('{0}/api/user/{1}/contact_details'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if contact_resp.status_code == 200:
        contact_json = contact_resp.json()
        contact_list = contact_json['contact_details']
    
    # Highest qualification Details
    hqual_json = {}
    hqual_list = {}
    hqual_resp = requests.get('{0}/api/user/{1}/highest_qualification'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if hqual_resp.status_code == 200:
        hqual_json = hqual_resp.json()
        hqual_list = hqual_json['highest_qualification']
    
    # Qualification Details
    qual_json = {}
    qual_list = {}
    qual_resp = requests.get('{0}/api/user/{1}/qualification'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if qual_resp.status_code == 200:
        qual_json = qual_resp.json()
        qual_list = qual_json['qualification']
    
    # Certification Details
    cert_json = {}
    cert_list = {}
    cert_resp = requests.get('{0}/api/user/{1}/certification'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if cert_resp.status_code == 200:
        cert_json = cert_resp.json()
        cert_list = cert_json['certifications']
    
    # Projects Details
    pro_json = {}
    pro_list = {}
    pro_resp = requests.get('{0}/api/user/{1}/project'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if pro_resp.status_code == 200:
        pro_json = pro_resp.json()
        pro_list = pro_json['projects']
    
    # Experience Details
    exp_json = {}
    exp_list = {}
    exp_resp = requests.get('{0}/api/user/{1}/experience'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if exp_resp.status_code == 200:
        exp_json = exp_resp.json()
        exp_list = exp_json['Experience']
    
     # Other Details
    oth_json = {}
    oth_list = {}
    oth_resp = requests.get('{0}/api/user/{1}/other_details'.format(host, user_id), headers={'Authorization': 'Bearer {}'.format(session['api_token'])})
    if oth_resp.status_code == 200:
        oth_json = oth_resp.json()
        oth_list = oth_json['other_details']

    
    resume = render_template("resume.html", title='Resume', user_id=user_id, demog_list=demog_list, contact_list=contact_list, hqual_list=hqual_list, qual_list=qual_list, cert_list=cert_list, pro_list=pro_list, exp_list=exp_list, oth_list=oth_list)
    filename =  user_name + '.pdf'

    pdfkit.from_string(resume, app.config["CREATED_RESUMES"] + '//' + filename)

    return send_from_directory(app.config["CREATED_RESUMES"],
                               filename)







with open( os.getcwd()+r'//Recruitize_Analysis_Data.json') as f:
  match_data = json.load(f)

def extract_resume_text(pdf_path):
    raw= parser.from_file(pdf_path)
    txt=''
    bullets=[]
    text_list=[]
    for line in io.StringIO(raw['content']):
            if len(line.strip())!=0:
                txt=txt+"\n"+line.strip()
                text_list.append(line.strip())
    return txt, text_list

def preprocess_text(txt):
    txt=txt.replace('/', " ").replace("-"," ").replace(',', ' ')
    for i in match_data['X']:
        txt=txt.replace(i,'X')
    for i in match_data['XII']:
        txt=txt.replace(i,'XII')
    words=nltk.word_tokenize(txt)
    wordsNS=[word for word in words if word not in stopwords.words('english') and word.isalnum() and word.isdigit()==False and word not in re.findall('[2][.][0-1][1-9]',txt) ]
    lemma=WordNetLemmatizer()
    txt_new=" ".join([lemma.lemmatize(word) for word in wordsNS])  
    return txt_new

def extract_name(resume_text):
    nlp = spacy.load('en_core_web_sm')
    matcher = Matcher(nlp.vocab)
    nlp_text = nlp(resume_text[:50])
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    matcher.add('NAME', None, pattern)
    matches = matcher(nlp_text)
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text
    
def extract_phoneNo(t):
    no= list(re.findall("[6-9][0-9]{9}", t))
    return int(no[0])

def extract_mobile_number(text):
    phone = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), text)
    
    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + number
        else:
            return number

def extract_email(t):
    email= re.findall('\S+@\S+[.][a-z]+', t)
    return email[0]

def extract_DOB(t):
    dob=None
    dob= re.findall('[0-9]+/[0-9]+/[0-9]+|[0-9]+-[0-9]+-[0-9]+|[0-9]+[.][0-9]+[.][0-9]+',t)
    return  dob[0]

def calculateAge(birthDate): 
    birthDate=datetime.datetime.strptime(birthDate.replace("/","").replace("-","").replace(".",""), '%d%m%Y').date()
    today = date.today()
    age = today.year - birthDate.year -  ((today.month, today.day) < (birthDate.month, birthDate.day)) 
    return age 

def extract_personalDetails(txt):
    dic={}
    pd=[]
    for line in txt.splitlines():
        split= re.split(":",line)
        word_tokens=word_tokenize(txt)
        if len(split)==2:
            string=split[0].strip()
            detail=split[1].strip()
            if re.match('name', string, re.IGNORECASE)!=None:
                dic["Name"]=detail
                pd.append(string);pd.extend(word_tokenize(detail))
            if re.search("gender", string, re.IGNORECASE)!=None:
                if re.search("f", detail, re.IGNORECASE)!=None:
                    dic["Gender"]="Female";
                elif re.search("m", detail, re.IGNORECASE)!=None:
                    dic["Gender"]="Male";
                pd.append(string);
            if re.search("contact" or "mobile" or "phone", string, re.IGNORECASE)!=None:
                try:
                    if detail[0]>=10:
                        dic["Contact No."]=detail[0]
                except: print("Contact Error")
                pd.append(string);pd.extend(detail)
            if re.search("mail", string, re.IGNORECASE)!=None:
                dic["E-Mail"]=detail
                pd.append(string);
                pd.extend(word_tokenize(detail))
            if re.search("address", string, re.IGNORECASE)!=None:
                dic["Address"]=detail                  
                pd.append(string);pd.extend(word_tokenize(detail))
            if re.search("father", string, re.IGNORECASE)!=None:
                dic["Father's Name"]=detail
                pd.append(string);pd.extend(word_tokenize(detail))
            if re.search("mother", string, re.IGNORECASE)!=None:
                dic["Mother's Name"]=detail
                pd.append(string);pd.extend(word_tokenize(detail))
            dob=None
            if re.search("dob" or "d.o.b", string, re.IGNORECASE)!=None:
                dic["DOB"]=detail;
    if "Name" not in dic.keys():
        dic["Name"]=extract_name(txt)
    if "Contact No." not in dic.keys():
        try:
            dic["Contact No."]=extract_phoneNo(txt)
        except:print("Contact Error")
    if "E-Mail" not in dic.keys():
        try:
            dic["E-Mail"]=extract_email(txt)
        except:print("E-mail Error")
    if "DOB" not in dic.keys():
        try:
            dic["DOB"]=extract_DOB(txt)
        except: print("DOB Error")
    try:    
        if "Age"  not in dic.keys() and "DOB" in dic.keys() and len(dic["DOB"])!=0:
            dic["Age"]=calculateAge(dic["DOB"])
    except: print("Error Age") 
    pd.extend(["Male","MALE", "Female","FEMALE"])
    return dic, pd
def extract_softwares(t):
    s=[]
    for software in match_data['Softwares']:
        if re.search(software, t, re.IGNORECASE)!=None:
            s.append(software)
    return s
def tokenize_resume(txt):
    word_tokens=word_tokenize(txt)
    stop_words = set(stopwords.words('english'))
    t= [w for w in word_tokens if not w in stop_words]
    return list(set(t))
def extract_programmingLanguages(txt):
    lang=set()
    tokens=tokenize_resume(txt)
    for i in range(len(match_data['Programming Languages'])):
        lang.add(match_data['Programming Languages'][i])
    return tokens.intersection(lang)
def create_wordcloud(t,path):
    resume_wordcloud =  WordCloud(width=600,height=600,background_color ='white',min_font_size=10).generate(t)                       
    plt.figure(figsize=(8,8),facecolor=None) 
    plt.imshow(resume_wordcloud) 
    plt.axis("off") 
    plt.tight_layout(pad=0) 
    plt.savefig(path)
    return path
def job_score(t, job):
    c=[]
    for i in match_data["Jobs"][job]:
        try:
            if re.search(i.lower(),t, re.IGNORECASE)!=None:
                c.append(i)
        except: c=[]       
    score=len(set(c))
    return score
def best_job(t):
    job_list=match_data["Jobs"].keys()
    jobs={}
    for i in job_list:
        jobs[i]=job_score(t, i)
    b_job = dict(sorted(jobs.items(), key=operator.itemgetter(1),reverse=True))
    best_job=list(b_job)
    return best_job[:3]
def extract_branch(t):
    branch=[]
    for b in match_data['Branches']:
        if re.search(b,t, re.IGNORECASE)!=None:
            branch.append(b)
    return branch
def extract_qualifications_Tabular(pdf_path):  
    dfs = tabula.read_pdf(pdf_path, stream=True, pages='all')
    data=dfs[0]
    data = data.dropna().reset_index(drop=True)
    col=data.columns
    for c in col:
        if re.search("year", c, re.IGNORECASE)!=None:
            data=data.rename(columns={c:"Year"})
        elif re.search("institut", c, re.IGNORECASE)!=None:
            data=data.rename(columns={c:"Institution"})
        elif re.search("quali" or "name" or 'degr', c, re.IGNORECASE)!=None:
            data=data.rename(columns={c:"Qualification"})
        elif re.search("gpa" or "perc", c, re.IGNORECASE)!=None:
            data=data.rename(columns={c:"Percentage"})

    for p in range(len(data["Percentage"])):
        try:
            s=data.at[p,"Percentage"]
            l=re.findall(r"\d+\.\d+",str(s))
            per=float(l[0])
            if per<10:
                per=per*9.5
            data.at[p,"Percentage"] = per
        except: print("Error ignored")
        data_dict = data.to_dict(orient='records')
    return data_dict
def extract_year1(txt):
    year=re.findall("[2][0]\d{2}|[1][9]\d{2}", txt, re.IGNORECASE)
    return  year

def extract_qualifications_nonTabular(txt):
    btech=re.findall("B.*Tech", str(txt), re.IGNORECASE)[0]
    btech_index=txt.index(btech)
    XII=re.findall("XII", txt[btech_index:], re.IGNORECASE)[0]
    XII_index=txt.index(XII)
    X=re.findall("X", txt[XII_index:], re.IGNORECASE)[1]
    X_index=txt.index(X,XII_index+1)
    x=re.findall("(X)", txt, re.IGNORECASE)
    xii=re.findall("XII", txt, re.IGNORECASE)[0]
    btech_data=txt[btech_index:XII_index]
    XII_data=txt[XII_index: X_index]
    X_data=txt[X_index:]
    btech_year=extract_year1(btech_data)
    btech_year_completion=max(btech_year)
    btech_gpa=float(re.findall("[0-9]{1,2}[.][0-9]{1,2}",btech_data)[0])
    XII_year=extract_year1(XII_data)
    XII_year_completion=max(XII_year)
    XII_gpa=float(re.findall("[0-9]{1,2}[.][0-9]{1,2}",XII_data)[0])
    X_year=extract_year1(X_data)
    X_year_completion=X_year[0]
    X_gpa=float(re.findall("[0-9]{1,2}[.][0-9]{1,2}",X_data)[0])
    li=[]
    dic={}
    dic["Qualification"]=btech
    if(btech_gpa<10):
        btech_gpa=btech_gpa*9.5
    dic["Percentage"]=btech_gpa
    dic["Year"]=btech_year_completion
    li.append(dic)
    dic={}
    dic["Qualification"]=XII
    if(XII_gpa<10):
        btech_gpa=btech_gpa*9.5
    dic["Percentage"]=XII_gpa
    dic["Year"]=XII_year_completion
    li.append(dic)
    dic={}
    dic["Qualification"]=X
    if(X_gpa<10):
        btech_gpa=btech_gpa*9.5
    dic["Percentage"]=X_gpa
    dic["Year"]=X_year_completion
    li.append(dic)
    dic={}
    return li

def count_words(txt):
    return int(len(txt.split()))
def count_freq(txt):
    L_AB=[txt,""]
    cv=CountVectorizer(ngram_range=(1,1), analyzer='word')
    cv_train=cv.fit(L_AB)
    ngram=cv.transform(L_AB)
    f=ngram.toarray()
    freq= dict(zip(cv_train.get_feature_names(), [int(i) for i in f[0]]))
    max_freq=dict(sorted(freq.items(), key=operator.itemgetter(1),reverse=True))
    max_freq=dict(list(max_freq.items())[0: 10])
    return max_freq
def find_jaccardDistance(s1,s2):
    dis = nltk.jaccard_distance(s1, s2)
    return dis
def extract_competency_score(t, tag):
    c=[]
    for i in match_data["Competencies"][tag]:
            if re.search(i.lower(),t, re.IGNORECASE)!=None:
                c.append(i)
    score=len(set(c))*10
    if score > 100:
        score=100
    return score
def extract_competencies(t):
    competency_list=match_data["Competencies"].keys()
    competencies={}
    for i in competency_list:
        competencies[i]=int(extract_competency_score(t,i))
    return competencies
def extract_skill_score(t, branch, skill):
    s=[]
    for i in match_data["Skills"][branch][skill]:
        try:
            if re.search(i.lower(),t, re.IGNORECASE)!=None:
                s.append(i)
        except:print(i)
    s=list(set(s))
    score=len(s)*10
    if score > 100:
        score=100
    if score>10:
        return {"Score":int(score),"Skills": s}
    else:return -1
def extract_skill(t):
    skill_branch=list(match_data["Skills"].keys())
    skill={}
    skillset={}
    #print(skill_branch)
    for i in skill_branch:
        skill={}
        for j in match_data["Skills"][i].keys():
            sk=extract_skill_score(t,i, j)
            if sk!=-1:
                skill[j]=sk
        if bool(skill):
            skillset[i]=skill
    return skillset
def compare_skills_jd_Resume(list_jd, list_cv):#pass list===skills/software list
    intrsection=list_jd.intersection(list_cv)
    dif=list_jd.difference(list_cv)
    matchScore=intrsection/list_jd*100
    return intrsection,matchScore, dif
#dif==additional skills/softwares required
#func returns all skills that matched, Match Percentage, Additional skills required
def extract_year(txt):
    year=re.findall("[2][0]\d{2}|[1][9]\d{2}",txt, re.IGNORECASE)
    y={}
    y['start']=min(year)
    y['end']=max(year)
    return  y
def convert_doc_to_soup(doc_path):
    with open(doc_path, "rb") as docx_file:
        result = mammoth.convert_to_html(docx_file)
        html = result.value # The generated HTML
        messages = result.messages 
        soup=BeautifulSoup(html,'html.parser')
    return soup

def extract_bold_from_soup(soup):
    table=soup.findAll(["strong","h1", "h2", "h3","h4","h5","h6"])
    bold=[]
    for i in table:
        bold.append(i.text)
    return bold
def extract_companies(bold_list):
    nlp = en_core_web_sm.load()
    company=[]
    for i in bold_list:
        doc = nlp(i)
        for X in doc.ents:
            if X.label_=='ORG' :
                if X.text not in company and len(X.text)>4:
                    company.append(X.text) 
    #company = list(dict.fromkeys(company))
    return company
def search_exp(bold_txt,companies):
    exp=[];s=[];e=[];
    for i in range(len(companies)-1):
        ind=bold_txt.index(companies[i])
        ind1=bold_txt.index(companies[i+1])
        #print(companies[i],"--")
        #print(ind, ind1)
        #print('----------')
        ex=[]
        try:
            y=extract_year(bold_txt[ind:ind1])
            if len(exp)==0:
                exp.append({"company":companies[i], "start":y['start'],"end":y['end']})
            elif y['end']<=exp[-1]['start']:
                    exp.append({"company":companies[i], "start":y['start'],"end":y['end']})
        except: -1
    try:
        ind=bold_txt.index(companies[i])
        y=extract_year(bold_txt[ind:ind+100])
        if y['end']<=exp[-1]['start']:
            exp.append({"company":companies[-1], "start":y['start'],"end":y['end']})
    except: -1
    return exp
def extract_links(soup):
    links=soup.findAll("a",href=True)
    link_list=[]
    for i in links:
        link_list.append(i['href'])
    return list(set(link_list))
def extract_certifications(links):
    certification={}
    site={"udemy","coursera","udacity"}
    for i in links:
        for j in site:
            if re.search(j,i, re.IGNORECASE):
                certification[j]=i
                break  
def extract_profiles(links):
    profile={}
    site={'linkedin',"github","hackerrank","codechef","topcoder"}
    for i in links:
        for j in site:
            if re.search(j,i, re.IGNORECASE):
                profile[j]=i
                break
def create_psychograph(text, path):
    cEXT = pickle.load( open(r"Personality_affinities/cEXT.p", "rb"))
    cNEU = pickle.load( open(r"Personality_affinities/cNEU.p", "rb"))
    cAGR = pickle.load( open(r"Personality_affinities/cAGR.p", "rb"))
    cCON = pickle.load( open(r"Personality_affinities/cCON.p", "rb"))
    cOPN = pickle.load( open(r"Personality_affinities/cOPN.p", "rb"))
    vectorizer_31 = pickle.load( open(r"Personality_affinities//vectorizer_31.p", "rb"))
    vectorizer_30 = pickle.load( open(r"Personality_affinities//vectorizer_30.p", "rb"))
    scentences = re.split("(?<=[.!?]) +", text)
    text_vector_31 = vectorizer_31.transform(scentences)
    text_vector_30 = vectorizer_30.transform(scentences)
    EXT = cEXT.predict(text_vector_31)
    NEU = cNEU.predict(text_vector_30)
    AGR = cAGR.predict(text_vector_31)
    CON = cCON.predict(text_vector_31)
    OPN = cOPN.predict(text_vector_31)
    
    predictions = [EXT, NEU, AGR, CON, OPN]
    sum=0
    for i in range(0,len(predictions[0])):    
            sum = sum + predictions[0][i]
    sum=(sum*100)/len(predictions[0])
    count=0
    for j in range(0, len(predictions[1])):    
          count = count + predictions[1][j]
    count=(count*100)/len(predictions[1])
    total=0
    for j in range(0, len(predictions[2])):    
          total = total + predictions[2][j]
    total=(total*100)/len(predictions[2])  
    cons=0
    for j in range(0, len(predictions[3])):    
          cons = cons + predictions[3][j]
    cons=(cons*100)/len(predictions[3])
    opnn=0
    for j in range(0, len(predictions[4])):    
          opnn = opnn + predictions[4][j]
    opnn=(opnn*100)/len(predictions[4])
    final=[int(sum),int(count),int(total),int(cons),int(opnn)]
    height = final
    likeability_scores = np.array(height)
    data_normalizer = mp.colors.Normalize()

    color_map = mp.colors.LinearSegmentedColormap("my_map", {"red": [(0, 0.50, 0.5),(1.0, 0, 0)],"green": [(0, 0.5, 0.5),(1.0, 0, 0)],"blue": [(0, 1.0, 1.0),(1.0, .5, .5)]})
    bars = ('Extrovert', 'Neuroticism', 'Agreeable', 'Conscientious', 'Openness')
    y_pos = np.arange(len(bars))
    plt.figure(figsize=(20,20),facecolor=None)
    plt.barh(y_pos, height,  color=color_map(data_normalizer(likeability_scores)),edgecolor="black",linewidth=3)
    plt.xlabel("Score(in %)", labelpad=20, weight='bold', size=18)
      
    plt.ylabel("Personality Affinities", labelpad=20, weight='bold', size=18)
    for i, v in enumerate(height):
        plt.text(v + 3, i + .25, str(v)+"%",va='center', color='black', size=12)

    plt.yticks(y_pos, bars, size=15)
    plt.title('Psychographic Analysis',size=18) 
    plt.savefig(path)
    return path

def Competenciespiechart(args,path):
    labels=args.keys()

    colors=['red','blue','yellow','pink','green','cyan','purple']
    fig1,ax1=plt.subplots(figsize=(10,10))
    
    #Explode:
    explode=(0.07,0.07,0.07,0.07,0.07,0.07,0.07)
    #Startangle 10 assume
    ax1.pie(args.values(),colors=colors,autopct='%1.1f%%',startangle=10,pctdistance=0.85,shadow=True,explode=explode
       ,textprops={'color':"black",'fontsize':20})
    circle=plt.Circle((0,0),0.80,fc='white')
    fig=plt.gcf()
    fig.gca().add_artist(circle)
    ax1.legend(labels,loc="center",fontsize=17)
    ax1.axis('equal')
    plt.tight_layout()
    plt.title('Competencies',fontsize=28)
    plt.savefig(path,bbox_inches='tight')
    return path


def create_user_json(filename,pdf_path):
    data={}

    t, t_list=extract_resume_text(pdf_path)
    data["No. of Words"]=count_words(t)
    data["Personal Details"],remove_list=extract_personalDetails(t)
    try:
        data["Qualifications"]=extract_qualifications_Tabular(pdf_path)
    except:
        try:
            data["Qualifications"]=extract_qualifications_nonTabular(t)
        except:print("Qualification Error")
    ptxt=preprocess_text(t)#preprocessed txt
    data["Competencies"]=extract_competencies(ptxt)
    wpd_txt=ptxt
    for i in remove_list:
        wpd_txt=wpd_txt.lower().replace(i.lower(),"")#wpd_txt=txt without personal details
    data["Max used Words"]=count_freq(wpd_txt)
    wcloudname = filename.rsplit(".", 1)[0]  + '.png'
    graph = filename.rsplit(".", 1)[0]  + '.png'
    wpath = app.config["CREATED_WORDCLOUDS"] + '//' + wcloudname
    gpath = app.config["CREATED_GRAPHS"] + '//' + graph
    pie = filename.rsplit(".", 1)[0]  + '.png'
    data["Word Cloud Path"]=create_wordcloud(wpd_txt,wpath)
    data["WCloudName"] = wcloudname
    data["GName"] = graph
    data["Pie"] = pie
    piepath = app.config["CREATED_PIE"] + '//' + pie
    data["PieChart"] = Competenciespiechart(data["Competencies"], piepath)
    try:
        data["Psychograph"]=create_psychograph(t, gpath)
    except:print("Psychograph Error")
    #try:
    docx_file = pdf_path.replace('.pdf','.docx')
    parse(pdf_path, docx_file, start=0)
    soup=convert_doc_to_soup(docx_file)
    bold_list=extract_bold_from_soup(soup)
    companies=extract_companies(bold_list)
    bold_txt=" ".join(bold_list)
    #try:
    data["Useful Links"]=extract_links(soup)
    data["Profile Links"]=extract_profiles(data["Useful Links"])
    data["Certifications"]=extract_certifications(data["Useful Links"])
    #except:print("Links Error")
    data["Skills"]=extract_skill(t)
    remove_list1=[]
    for i in data['Skills'].keys():
        for j in data['Skills'][i].keys():
            remove_list1+=data['Skills'][i][j]["Skills"]
    
  
    return data