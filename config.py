import os

DEBUG = True

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if os.environ.get('SECRET_KEY'):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SECRET_KEY')
else:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'secretshhhh'
QUERY_URL = 'http://h4ibootcamp2k17.herokuapp.com'
