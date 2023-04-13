import pytest
from spyglasses.models import User, Post, db
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash


test_username = 'user1'
test_password = 'password'


class CustomTestClient(FlaskClient):
    def __init__(self, *args, **kwargs):
        self.access_token = None
        super(CustomTestClient, self).__init__(*args, **kwargs)

    def create_user_and_login(self, username=test_username, password=test_password):
        get_or_create_user(username, password)
        response = self.post('/api/login', json={
            'username': username,
            'password': password
        })
        json_data = response.get_json()
        self.access_token = json_data['access_token']

    def open(self, *args, **kwargs):
        if self.access_token:
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f'Bearer {self.access_token}'
            kwargs['headers'] = headers
        return super(CustomTestClient, self).open(*args, **kwargs)


def get_or_create_user(username=test_username, password=test_password):
    user = User.query.filter_by(username=username).first()
    if user is None:
        hashed_password = generate_password_hash(password)
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
    return user


def create_post(**kwargs):
    if 'user' not in kwargs:
        kwargs['user'] = get_or_create_user()
    post = Post(**kwargs)
    db.session.add(post)
    db.session.commit()
    return post
