import json
import pytest
from spyglasses import create_test_app
from spyglasses.models import db, Post


def create_post():
    post = Post(content='Test content', post_type='public')
    db.session.add(post)
    db.session.commit()
    return post


@pytest.fixture
def client():
    app = create_test_app()
    app_context = app.app_context()
    app_context.push()
    db.create_all()

    # Create sample data
    post1 = Post(content="Test post 1 content",
                 blurb="Test post 1 blurb", post_type="text")
    post2 = Post(content="Test post 2 content",
                 blurb="Test post 2 blurb", post_type="text")
    db.session.add_all([post1, post2])
    db.session.commit()

    yield app.test_client()

    db.session.remove()
    db.drop_all()
    app_context.pop()


def test_get_posts(client):
    response = client.get('/api/posts')
    assert response.status_code == 200
    data = response.json
    assert len(data) == 2
    for post in data:
        assert 'content' not in post
        assert 'id' in post
        assert 'blurb' in post
        assert 'post_type' in post
        assert 'created_at' in post
        assert 'updated_at' in post


def test_create_post(client):
    # Test creating a post with valid data
    data = {
        'content': 'This is a test post.',
        'post_type': 'public'
    }
    response = client.post(
        '/api/posts', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert 'post_id' in response_data
    assert 'message' in response_data
    assert response_data['message'] == 'Post created successfully'

    # Test creating a post with missing data
    data = {
        'content': 'This is another test post.'
    }
    response = client.post(
        '/api/posts', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert 'error' in response_data
    assert response_data['error'] == 'Missing content or post_type in request data'


def test_get_post(client):
    post = create_post()

    response = client.get(f'/api/posts/{post.id}')
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data['content'] == 'Test content'
    assert response_data['post_type'] == 'public'

    response = client.get('/api/posts/9999')
    assert response.status_code == 404


def test_update_post(client):
    post = create_post()
    updated_data = {
        "blurb": "Updated blurb",
        "content": "Updated content",
        "post_type": "article"
    }
    response = client.put(f'/api/posts/{post.id}', json=updated_data)
    json_data = response.get_json()

    assert response.status_code == 200
    assert json_data["blurb"] == updated_data["blurb"]
    assert json_data["content"] == updated_data["content"]
    assert json_data["post_type"] == updated_data["post_type"]
