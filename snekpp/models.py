from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from .main import db

class LeaderboardSingle(db.Model):
    userid = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    highScore = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Text, nullable=False, primary_key=True)

    user = db.relationship('User', backref='user_single', foreign_keys=[userid])

    def __repr__(self):
        return '<Single Score Entry {} {} {}>'.format(self.userid, self.highScore, self.date)


class LeaderboardMulti(db.Model):
    userid = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    highScore = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Text, nullable=False, primary_key=True)

    user = db.relationship('User', backref='user_multi', foreign_keys=[userid])

    def __repr__(self):
        return '<Muli Score Entry {} {} {}>'.format(self.userid, self.highScore, self.date)


class Follow(db.Model):
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    status =  db.Column(db.Integer, nullable=False)

    requester = db.relationship('User', backref='user_req', foreign_keys=[requester_id])
    receiver = db.relationship('User', backref='friend_req', foreign_keys=[receiver_id])

    def __repr__(self):
        return '<Follow {} {} {}>'.format(self.requester_id, self.receiver_id, self.status)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    single_highscore = db.Column(db.Integer, nullable=False, default=0)
    mult_highscore = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
