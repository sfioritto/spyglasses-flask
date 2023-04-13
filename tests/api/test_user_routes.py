import pytest
from flask import Flask
from spyglasses import create_test_app
from spyglasses.models import db
from tests.api import get_or_create_user, CustomTestClient


@pytest.fixture
def client():
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


def test_create_user(client):
    response = client.post(
        '/api/user', json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 201
    assert response.get_json()["username"] == "testuser"


# def test_create_user_missing_fields(client):
#     response = client.post('/api/user', json={"username": "testuser"})
#     assert response.status_code == 400


def test_get_user(client):
    user = get_or_create_user()

    response = client.get(f'/api/user/{user.id}')
    assert response.status_code == 200
    assert response.get_json()["username"] == user.username


def test_get_user_not_found(client):
    response = client.get('/api/user/200')
    assert response.status_code == 404


def test_update_user(client):
    user = get_or_create_user()

    response = client.put(
        f'/api/user/{user.id}', json={"username": "updateduser"})
    assert response.status_code == 200
    assert response.get_json()["username"] == "updateduser"


def test_update_user_nothing_to_update(client):
    user = get_or_create_user()

    response = client.put(f'/api/user/{user.id}', json={})
    assert response.status_code == 400


def test_delete_user(client):
    user = get_or_create_user()

    response = client.delete(f'/api/user/{user.id}')
    assert response.status_code == 200
    assert response.get_json()["result"] == "User deleted"


def test_delete_user_not_found(client):
    response = client.delete('/api/user/200')
    assert response.status_code == 404
