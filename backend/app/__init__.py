from flask import Flask
from flask_cors import CORS

app = Flask(__name__, static_folder='../frontend/dist', template_folder='../frontend/dist')
CORS(app)

from app.routes import *
