import pytest
from flask import Flask
from spyglasses import create_test_app
from spyglasses.models import db
from tests.api import get_or_create_user, CustomTestClient


@pytest.fixture
def user():
    user = get_or_create_user()
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def test_client():
    app = create_test_app()
    app_context = app.app_context()
    app_context.push()
    db.create_all()

    Flask.test_client_class = CustomTestClient
    with app.test_client() as client:
        client.create_user_and_login()

    yield client

    db.session.remove()
    db.drop_all()
    app_context.pop()
