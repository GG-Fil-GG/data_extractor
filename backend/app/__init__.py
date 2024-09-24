import os
from flask import Flask
from flask_cors import CORS

def create_app():
    # Get the absolute path to the frontend/dist directory
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/dist'))
    app = Flask(__name__, static_folder=static_dir, template_folder=static_dir)
    
    CORS(app, resources={r"/*": {"origins": "*"}})

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app