import json
from spyglasses.models import Post
from tests.api import create_post


def test_get_posts(test_client, user):
    test_client.post(
        '/api/posts', json={'content': 'Test content', 'type': 'public'})
    test_client.post(
        '/api/posts', json={'content': 'Test content 2', 'type': 'public'})
    response = test_client.get('/api/posts')
    assert response.status_code == 200
    data = response.json
    assert len(data) == 2
    for post in data:
        assert 'content' not in post
        assert 'id' in post
        assert 'blurb' in post
        assert 'type' in post
        assert 'created_at' in post
        assert 'updated_at' in post


def test_create_post(test_client):
    # Test creating a post with valid data
    data = {
        'content': 'This is a test post.',
        'type': 'public'
    }
    response = test_client.post(
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
    response = test_client.post(
        '/api/posts', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert 'error' in response_data
    assert response_data['error'] == 'Missing content or type in request data'


def test_get_post(test_client):
    post = create_post(content='Test content', type='public')

    response = test_client.get(f'/api/posts/{post.id}')
    assert response.status_code == 200
    response_data = json.loads(response.data)
    print(response_data)
    assert response_data['content'] == 'Test content'
    assert response_data['type'] == 'public'

    response = test_client.get('/api/posts/9999')
    assert response.status_code == 404


def test_update_post(test_client):
    post = create_post(content='Test content', type='public')
    updated_data = {
        "blurb": "Updated blurb",
        "content": "Updated content",
        "type": "external"
    }
    response = test_client.put(f'/api/posts/{post.id}', json=updated_data)
    json_data = response.get_json()

    assert response.status_code == 200
    assert json_data["blurb"] == updated_data["blurb"]
    assert json_data["content"] == updated_data["content"]
    assert json_data["type"] == updated_data["type"]


def test_delete_post(test_client):
    post = create_post(content='Test content', type='public')
    response = test_client.delete(f'/api/posts/{post.id}')
    deleted_post = Post.query.get(post.id)
    json_data = response.get_json()

    assert response.status_code == 200
    assert deleted_post is None
    assert json_data["message"] == "Post deleted"


def test_create_note(test_client):
    post = create_post(content='Test content', type='public')
    note_data = {"content": "This is a sample note content."}
    response = test_client.post(f'/api/posts/{post.id}/notes', json=note_data)
    json_data = response.get_json()

    assert response.status_code == 201
    assert json_data["message"] == "Note created successfully"
    assert "note_id" in json_data
