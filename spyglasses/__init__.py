from flask import Flask
from flask_cors import CORS


def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # app.config.from_pyfile("config.py", silent=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spyglasses.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    else:
        # load the test config if passed in
        app.config.update(test_config)

    from spyglasses import views
    app.register_blueprint(views.bp)

    from spyglasses.models import db
    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app
