import os
import importlib
import pkgutil
from os import environ as env
from flask import Flask
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask_session import Session


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
            dev_user = User.query.filter_by(auth_user_id='dev').first()

            # If the dev user does not exist, create one
            if dev_user is None:
                dev_user = User(
                    given_name='dev',
                    family_name='developer',
                    email='dev@test.com',
                    auth_user_id='dev'
                )
                db.session.add(dev_user)
                db.session.commit()


def create_app(api_version=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spyglasses.db'
    app.secret_key = env.get("APP_SECRET_KEY")
    CORS(app, supports_credentials=True,
         origins='*',
         allow_headers=["Content-Type", "Content-Encoding", "Authorization"],
         methods=["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"])

    ENV_FILE = find_dotenv()
    if ENV_FILE:
        load_dotenv(ENV_FILE)

    oauth = OAuth(app)

    auth0 = oauth.register(
        "auth0",
        client_id=env.get("AUTH0_CLIENT_ID"),
        client_secret=env.get("AUTH0_CLIENT_SECRET"),
        client_kwargs={
            "scope": "openid profile email",
        },
        server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
    )

    app.oauth = oauth
    app.auth0 = auth0

    register_views(app)
    register_api(app, api_version)
    init_db(app)
    return app


def create_test_app():
    # Use the environment variable SPYGLASSES_API_VERSION, if it exists.
    api_version = os.environ.get('SPYGLASSES_API_VERSION', None)
    app = create_app(api_version)
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app
