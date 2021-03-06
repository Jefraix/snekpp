from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)

app.config['SECRET_KEY'] = 'snakesarekewl'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///snek.sqlite'

app.static_folder = 'static'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from .mainr import mainr as mainr_blueprint
app.register_blueprint(mainr_blueprint)

from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
