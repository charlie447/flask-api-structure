from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlalchemy
from sqlalchemy.ext.declarative import api

# logging
import logging
from logging.handlers import RotatingFileHandler
import os

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
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        '''The `RotatingFileHandler` class is nice because it rotates the logs,
            ensuring that the log files do not grow too large
            when the application runs for a long time. 
        '''
        file_handler = RotatingFileHandler('logs/application.log', maxBytes=10240,
                                       backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        '''logging categories, they are DEBUG, INFO, WARNING, ERROR and CRITICAL
            in increasing order of severity.
        '''
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')

    return app

from app import models