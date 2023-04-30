import pytest
from tests.api import get_or_create_user
from spyglasses import create_test_app


@pytest.fixture(scope='module')
def test_client():
    flask_app = create_test_app()

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            yield testing_client


def test_login_logout(test_client):
    user = get_or_create_user(username="dev", password="test")
    # test successful login
    response = test_client.post(
        '/api/login', json={"username": "dev", "password": "test"})
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'access_token' in json_data

    # test unsuccessful login
    response = test_client.post(
        '/api/login', json={"username": "dev", "password": "wrong"})
    assert response.status_code == 401

    # test successful logout
    response = test_client.post('/api/token/logout')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['msg'] == "Token has been revoked"

    # test unsuccessful logout (with no JWT)
    response = test_client.post('/api/token/logout')
    assert response.status_code == 401
