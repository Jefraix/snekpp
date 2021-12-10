from flask import render_template, request, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from .forms import RegistrationForm, LoginForm
from .models import User, Follow
from .main import db

auth = Blueprint('auth', __name__)

@auth.route('/user_signin', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('mainr.profile'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid user or password")
            return redirect(url_for('auth.login'))
        login_user(user)
        return redirect(url_for('mainr.profile'))
    return render_template('user_signin.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('mainr.index'))

@auth.route('/user_register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('mainr.profile'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('user_register.html', form=form)

@auth.route('/follow_request', methods=['POST'])
def follow():
    requestedUsername = request.form['friendUsername']
    friendUser =  User().query.filter_by(username=requestedUsername).first()
    previousFriendRequest = Follow.query.filter_by(requester_id=current_user.id,  
                                                          receiver_id=friendUser.id, status=1).first()
    
    if(previousFriendRequest is None):
        friendRequest = Follow(requester_id= current_user.id, 
                                      receiver_id=friendUser.id, status= 1)     
        db.session.add(friendRequest)  
        db.session.commit()
        return redirect(url_for('mainr.public_profile', queryUser=friendUser.username))
    else:
        Follow.query.filter_by(requester_id=current_user.id, receiver_id=friendUser.id, status=1).delete()
        db.session.commit()
        return redirect(url_for('mainr.public_profile', queryUser=friendUser.username))


@auth.route("/search", methods=['POST'])
@login_required
def search():
    search_username = request.form['friendUsername']
    search_user = User.query.filter_by(username= search_username).first()
    if search_user is None:
        return redirect(url_for('mainr.profile'))
    else:
        return redirect(url_for('mainr.public_profile', queryUser=search_username))