from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# instantiate flask app
app = Flask(__name__)

app.config.from_object('config')

db = SQLAlchemy(app)

from app.models.coordinates import *
from app.views.routes import *
