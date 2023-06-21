from app import app
from firebase_admin import credentials, initialize_app, storage, firestore
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

#==================================Firebase======================================
#Firebase config:
cred = credentials.Certificate(os.environ.get('FIREBASE_KEY_PATH'))
initialize_app(cred, {'storageBucket': os.environ.get('FIREBASE_BUCKET_PATH')})
#Firebase instances
db = firestore.client()
bucket = storage.bucket()
#================================================================================

#===============================Users Database===================================
#Database instances:
dbUser = SQLAlchemy(app)
migrate = Migrate(app, dbUser, render_as_batch=True)
#Database Model:
class User(dbUser.Model, UserMixin):
    id = dbUser.Column(dbUser.Integer, primary_key=True)
    uid = dbUser.Column(dbUser.String, nullable = False, unique = True)
    name = dbUser.Column(dbUser.String(100), nullable = False)
    email = dbUser.Column(dbUser.String(100), nullable = False, unique = True)
    password_hash = dbUser.Column(dbUser.String(100), nullable = False)
    current = dbUser.Column(dbUser.String(100))
    date_added = dbUser.Column(dbUser.DateTime, default = datetime.utcnow)

    def __init__(self, name, email, password, uid):
        self.name = name
        self.email = email
        self.password_hash = password
        self.uid = uid

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return '<Name %r>' % self.name
#================================================================================

#==================================FlaskLogin====================================
#Login Instances:
login_manager = LoginManager()
login_manager.init_app(app)
#Login Config:
login_manager.login_view = 'login'
login_manager.login_message = 'Acesso negado.'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
#================================================================================