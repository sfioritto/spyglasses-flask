import pytest
from flask import json
from spyglasses import create_test_app
from spyglasses.models import User, db


@pytest.fixture
def client():
    app = create_test_app()
    app_context = app.app_context()
    app_context.push()
    db.create_all()

    yield app.test_client()

    db.session.remove()
    db.drop_all()
    app_context.pop()


def test_create_user(client):
    response = client.post(
        '/api/user', json={"username": "testuser"})
    assert response.status_code == 201
    assert response.get_json()["username"] == "testuser"


# def test_create_user_missing_fields(client):
#     response = client.post('/api/user', json={"username": "testuser"})
#     assert response.status_code == 400


def test_get_user(client):
    user = User(username="testuser")
    db.session.add(user)
    db.session.commit()

    response = client.get(f'/api/user/{user.id}')
    assert response.status_code == 200
    assert response.get_json()["username"] == "testuser"


def test_get_user_not_found(client):
    response = client.get('/api/user/1')
    assert response.status_code == 404


def test_update_user(client):
    user = User(username="testuser")
    db.session.add(user)
    db.session.commit()

    response = client.put(
        f'/api/user/{user.id}', json={"username": "updateduser"})
    assert response.status_code == 200
    assert response.get_json()["username"] == "updateduser"


def test_update_user_nothing_to_update(client):
    user = User(username="testuser")
    db.session.add(user)
    db.session.commit()

    response = client.put(f'/api/user/{user.id}', json={})
    assert response.status_code == 400


def test_delete_user(client):
    user = User(username="testuser")
    db.session.add(user)
    db.session.commit()

    response = client.delete(f'/api/user/{user.id}')
    assert response.status_code == 200
    assert response.get_json()["result"] == "User deleted"


def test_delete_user_not_found(client):
    response = client.delete('/api/user/1')
    assert response.status_code == 404
