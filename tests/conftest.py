import pytest
from spyglasses import create_test_app
from spyglasses.models import db


@pytest.fixture
def test_client():
    app = create_test_app()
    app_context = app.app_context()
    app_context.push()
    db.create_all()

    with app.test_client() as client:
        with app.app_context():
            yield client

    db.session.remove()
    db.drop_all()
    app_context.pop()
