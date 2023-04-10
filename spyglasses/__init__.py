import os
from flask import Flask
from flask_cors import CORS


def make_app():
    app = Flask(__name__)
    CORS(app)
    return app


def register_views(app, url_prefix='/api'):
    from spyglasses import views
    app.register_blueprint(views.bp, url_prefix=url_prefix)


def init_db(app):
    from spyglasses.models import db
    db.init_app(app)
    with app.app_context():
        db.create_all()


def create_test_app():
    # Use the environment variable SPYGLASSES_API_VERSION, if it exists.
    # api_version = os.environ.get('SPYGLASSES_API_VERSION', None)
    # will use this to run specific versions of the API per run
    # of the test suite
    app = make_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    register_views(app)
    init_db(app)
    return app


def create_app():
    app = make_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spyglasses.db'
    api_prefix = f"/api/v{api_version}" if api_version else None
    register_views(app, **({"url_prefix": api_prefix} if api_prefix else {}))
    init_db(app)
    return app
