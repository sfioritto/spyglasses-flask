import os
import importlib
import pkgutil
from flask import Flask
from flask_cors import CORS


def make_app():
    app = Flask(__name__)
    CORS(app)
    return app


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
    from spyglasses.models import db
    db.init_app(app)
    with app.app_context():
        db.create_all()


def create_test_app():
    # Use the environment variable SPYGLASSES_API_VERSION, if it exists.
    api_version = os.environ.get('SPYGLASSES_API_VERSION', None)
    app = make_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    register_views(app)
    register_api(app, api_version=api_version)
    init_db(app)
    return app


def create_app():
    app = make_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spyglasses.db'
    register_views(app)
    register_api(app)
    init_db(app)
    return app
