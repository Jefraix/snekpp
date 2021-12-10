from flask import render_template, Blueprint, request, redirect, url_for, flash
from flask_login import current_user, login_required
from .models import Follow, User, LeaderboardSingle, LeaderboardMulti
from .main import db
from datetime import date
from .forms import EmailForm, PasswordRecoveryForm
import smtplib

mainr = Blueprint('mainr', __name__)

@mainr.route('/')
@mainr.route('/index')
def index():
    return render_template('index.html')

@mainr.route('/profile')
@login_required
def profile():
    return render_template('profile.html', 
        username=current_user.username, 
        sphs=current_user.single_highscore,
        mphs=current_user.mult_highscore)

@mainr.route('/singleplayer')
@login_required
def singleplayer():
    return render_template('singleplayer.html', 
        username=current_user.username)

@mainr.route('/multiplayer')
@login_required
def multiplayer():
    return render_template('multiplayer.html', 
        username=current_user.username)

@mainr.route('/score', methods=['POST'])
def score():
    user_name = request.form["username"]
    user = User.query.filter_by(username=user_name).first()
    if user is None:
        return "", 422
    old_score = user.single_highscore
    new_score = int(request.form["newScore"])
    if old_score < new_score:
        user.single_highscore = new_score
        ls_entry = LeaderboardSingle(userid=user.id, highScore=new_score, date=date.today())
        LeaderboardSingle.query.filter_by(userid=user.id).delete()
        db.session.add(ls_entry)
        db.session.commit()
    return "", 204

@mainr.route('/score_mult', methods=['POST'])
def score_mult():
    user_name = request.form["username"]
    user = User.query.filter_by(username=user_name).first()
    if user is None:
        return "", 422
    new_score = user.mult_highscore + 1
    user.mult_highscore = User.mult_highscore + 1
    lm_entry = LeaderboardMulti(userid=user.id, highScore=new_score, date=date.today())
    LeaderboardMulti.query.filter_by(userid=user.id).delete()
    db.session.add(lm_entry)
    db.session.commit()
    return "", 204

#12/07 Jose's magnificent work
#TODO If we add the ability to change profile picture we need to pass that parameter
@mainr.route('/users/<queryUser>',  methods=['GET', 'POST'])
@login_required
def public_profile(queryUser):
    public_user = User.query.filter_by(username= queryUser).first()
    if public_user.username is current_user.username:
        return redirect(url_for('mainr.profile', 
            username=current_user.username, 
            sphs=current_user.single_highscore,
            mphs=current_user.mult_highscore))
    elif public_user is None:
        return render_template('404.html'), 404
    
    isFriends = Follow.query.filter_by(requester_id=current_user.id, receiver_id=public_user.id).first()
    if isFriends is None:
        return render_template('publicProfile.html', 
            username=public_user.username, 
            sphs=public_user.single_highscore,
            mphs=public_user.mult_highscore, 
            visiting_user=current_user.username,
            status=0)
    else:
        friendStatus = isFriends.status
        return render_template('publicProfile.html', 
            username=public_user.username, 
            sphs=public_user.single_highscore,
            mphs=public_user.mult_highscore,
            visiting_user=current_user.username,
            status=friendStatus)

@mainr.route('/leaderboard_single_follow')
@login_required
def leaderboard_single_follow():
    listOfFollows = Follow.query.filter_by(requester_id=current_user.id).subquery()
    ls_entries = db.session.query(User.username, LeaderboardSingle.highScore, LeaderboardSingle.date)\
        .join(User, User.id == LeaderboardSingle.userid)\
        .join(listOfFollows, listOfFollows.c.receiver_id==LeaderboardSingle.userid).all()
    return render_template('leaderboard_single.html', stuff=ls_entries)

@mainr.route('/leaderboard_multi_follow')
@login_required
def leaderboard_multi_follow():
    listOfFollows = Follow.query.filter_by(requester_id=current_user.id).subquery()
    ls_entries = db.session.query(User.username, LeaderboardMulti.highScore, LeaderboardMulti.date)\
        .join(User, User.id == LeaderboardMulti.userid)\
        .join(listOfFollows, listOfFollows.c.receiver_id==LeaderboardMulti.userid).all()
    return render_template('leaderboard_multi.html', stuff=ls_entries)

@mainr.route('/leaderboard_single')
def leaderboard_single():
    ls_entries = db.session.query(User.username, LeaderboardSingle.highScore, LeaderboardSingle.date)\
        .join(User, User.id == LeaderboardSingle.userid).all()
    return render_template('leaderboard_single.html', stuff=ls_entries)


@mainr.route('/leaderboard_multi')
def leaderboard_multi():
    lm_entries = db.session.query(User.username, LeaderboardMulti.highScore, LeaderboardMulti.date)\
        .join(User, User.id == LeaderboardMulti.userid).all()
    return render_template('leaderboard_multi.html', stuff=lm_entries)

def send_reset_email(user):
    sender_email = 'alternatemail822@gmail.com'
    receiver_email = user.email
    token = user.password_hash
    #token = token_generator()
    password = 'theoSucks69'

    subject = "Reset Password Link for Snek++"
    text = "Click on this link to reset your password: " + "https://snekpp.herokuapp.com/password_recovery/" + token
    message = 'Subject: {}\n\n{}'.format(subject, text)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)

@mainr.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    form = EmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('forgot_password.html', form=form)

@mainr.route("/password_recovery/<token>", methods=['GET', 'POST'])
def password_recovery(token):
    print("test")
    #if current_user.is_authenticated:
        #return redirect(url_for('auth.login'))
    form = PasswordRecoveryForm()
    if form.validate_on_submit():
        user = User.query.filter_by(password_hash = token).first()
        user.set_password(form.password.data)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('password_recovery.html', form=form)
