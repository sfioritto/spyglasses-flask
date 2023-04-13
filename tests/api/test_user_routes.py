from tests.api import get_or_create_user


def test_create_user(test_client):
    response = test_client.post(
        '/api/user', json={"username": "test_create_user", "password": "testpassword"})
    assert response.status_code == 201
    assert response.get_json()["username"] == "test_create_user"


def test_create_user_missing_fields(test_client):
    response = test_client.post('/api/user', json={"username": "testuser"})
    assert response.status_code == 400


def test_get_user(test_client):
    user = get_or_create_user()

    response = test_client.get(f'/api/user/{user.id}')
    assert response.status_code == 200
    assert response.get_json()["username"] == user.username


def test_get_user_not_found(test_client):
    response = test_client.get('/api/user/200')
    assert response.status_code == 404


def test_update_user(test_client):
    user = get_or_create_user()

    response = test_client.put(
        f'/api/user/{user.id}', json={"username": "updateduser"})
    assert response.status_code == 200
    assert response.get_json()["username"] == "updateduser"


def test_update_user_nothing_to_update(test_client):
    user = get_or_create_user()

    response = test_client.put(f'/api/user/{user.id}', json={})
    assert response.status_code == 400


def test_delete_user(test_client):
    user = get_or_create_user()

    response = test_client.delete(f'/api/user/{user.id}')
    assert response.status_code == 200
    assert response.get_json()["result"] == "User deleted"


def test_delete_user_not_found(test_client):
    response = test_client.delete('/api/user/200')
    assert response.status_code == 404
