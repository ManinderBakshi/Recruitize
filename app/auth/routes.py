from flask import render_template, redirect, flash, url_for, request, session, make_response
from flask_login import current_user, login_user, login_required, logout_user
from app.model import User
from werkzeug.urls import url_parse
from app.auth import bp
from flask_mail import Message
from app import mail, app, db
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
import requests


host = 'http://127.0.0.1:5000'


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/signup', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    username = form.username.data
    email = form.email.data
    password = form.password.data
    recruiter = form.recruiter.data
    sign_up_response = requests.post('{0}/api/signup'.format(host), json={
        "username": username, "email": email, "password": password, "recruiter":recruiter})

    if sign_up_response.status_code == 400:
        sign_up_response_dict = sign_up_response.json()
        flash(sign_up_response_dict.get('msg'))
        return redirect(url_for('auth.register'))

    if sign_up_response.status_code == 200:
        return redirect(url_for('main.index'))

    return render_template('auth/register.html', title='Register', form=form)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    print('tokennnnnn',token)
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('auth.reset_password', token=token, _external=True)}
    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('main.index'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)
