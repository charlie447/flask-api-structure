from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlalchemy
from sqlalchemy.ext.declarative import api

from config import Config, DevelopmentConfig, ProductionConfig

db = SQLAlchemy()
migrate = Migrate()

def create_app(config=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprint
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='auth')

    return app

from app import models