import os
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv

from .models import db
from .auth import auth_bp
from .users import users_bp
from .devices import devices_bp
from .parkinson import parkinson_bp
# import your launcher
from .websocket.server import launch_in_thread

def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
            SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URI', 'sqlite:///app.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    CORS(app)
    db.init_app(app)
    Migrate(app, db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(parkinson_bp)
    
    @app.route('/')
    def index():
        return {'message': 'API is working!'}, 200

    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' and not test_config:
        from .websocket.server import launch_in_thread
        launch_in_thread(app)

    return app

