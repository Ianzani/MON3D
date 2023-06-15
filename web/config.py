import os

DEBUG = True
SECRET_KEY = os.environ.get('FIREBASE_KEY_PATH')
SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'