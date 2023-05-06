import os
import importlib
import pkgutil
from werkzeug.security import generate_password_hash
from flask import Flask
from flask_cors import CORS


def register_api(app, api_version=None):
    # If the api_version is specified, then
    # only register that version of the API.
    if api_version:
        api_module = importlib.import_module(f"spyglasses.api.v{api_version}")
        app.register_blueprint(api_module.bp, url_prefix='/api')
    else:
        # This iterates through all of the versions
        # in the spyglasses.api modeule and registers
        # them with the app.
        from spyglasses import api

        if os.environ.get('SPYGLASSES_ENVIRONMENT', None) == "DEVELOPMENT":
            # Register the most recent api version
            app.register_blueprint(api.bp, name="default", url_prefix='/api')

        # Iterate through all the submodules in the spyglasses.api package
        module_names = [module_name for _, module_name,
                        _ in pkgutil.iter_modules(api.__path__)]
        for module_name in module_names:
            if module_name.startswith('v'):
                # Import the submodule
                module = importlib.import_module(
                    f'spyglasses.api.{module_name}')
                # Register the blueprint with the app
                app.register_blueprint(
                    module.bp, url_prefix=f'/api/{module_name}')


def register_views(app):
    from spyglasses import views
    app.register_blueprint(views.bp)


def init_db(app):
    from spyglasses.models import db, User
    db.init_app(app)
    with app.app_context():
        db.create_all()

        # Check if the SPYGLASSES_ENVIRONMENT is true and create a dev user
        if os.environ.get('SPYGLASSES_ENVIRONMENT', None) == 'DEVELOPMENT':
            dev_user = User.query.filter_by(username='dev').first()

            # If the dev user does not exist, create one
            if dev_user is None:
                dev_user = User(
                    username='dev', password=generate_password_hash('test'))
                db.session.add(dev_user)
                db.session.commit()


def create_app(api_version=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spyglasses.db'
    CORS(app, supports_credentials=True,
         origins='*',
         allow_headers=["Content-Type", "Content-Encoding", "Authorization"],
         methods=["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"])

    register_views(app)
    register_api(app, api_version)
    init_db(app)
    return app


def create_test_app():
    api_version = os.environ.get('SPYGLASSES_API_VERSION', None)
    app = create_app(api_version)
    # Use the environment variable SPYGLASSES_API_VERSION, if it exists.
    api_version = os.environ.get('SPYGLASSES_API_VERSION', None)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app
