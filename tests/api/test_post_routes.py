import base64
import json
import gzip
from spyglasses.models import Post
from tests.api import create_post

html = """<html><head><title>Ahmad Jamal, measured maestro of the jazz piano, dies at 92</title></head><body><article><p>For most jazz performers, a song is part of a performance. For Ahmad Jamal, each song was a performance. Over the course of a remarkable eight-decade career, Jamal, who passed away Sunday at the age of 92, created stellar recordings both as an ambitious youth and a sagely veteran.</p>

<p>Jamal's death was confirmed by his daughter, Sumayah Jamal. He died Sunday afternoon in Ashley Falls, Mass., after a battle with prostate cancer.</p>

<p>Jamal's influence and admirers spread far and wide in jazz. For instance, Miles Davis found enormous inspiration in his work: In his 1989 autobiography, Miles, the legendary trumpeter said that Jamal "knocked me out with his concept of space, his lightness of touch, his understatement, and the way he phrases notes and chords and passages." Miles went on to record Jamal's "New Rhumba" on his classic 1957 recording Miles Ahead.</p>

<p>His contemporary admirers are just as fervent. Pianist Ethan Iverson, a founding member of the exceptionally popular trio The Bad Plus, said, "All of his pieces are theatrical and contained. In some ways the Bad Plus was an extension of his classic trio.</p>

<p>Pianist Vijay Iyer was just as adamant. "His sense of time is that of a dancer, or a comedian. His left hand stays focused, and his right hand is always in motion, interacting with, leaning on, and shading the pulse.</p>

<p>"He bends any song to his will, always open to the moment and always pushing the boundaries, willing to override whatever old chestnut he's playing in search of something profoundly alive."</p>

<p>Jamal was born Frederick Russell Jones in Pittsburgh on July 2, 1930. When he was 3 years old, his uncle challenged him to duplicate what he was playing on the piano, and the youngster actually could. He began formal studies of the piano at the age of 7 and quickly took on an advanced curriculum. He told Eugene Holley Jr. of Wax Poetics in a 2018 interview, "I studied Art Tatum, Bach, Beethoven, Count Basie, John Kirby, and Nat Cole. I was studying Liszt. I had to know European and American classical music. My mother was rich in spirit, and she led me to another rich person: my teacher, Mary Cardwell Dawson, who started the first African-American opera company in the country."</p>

<p>Jamal grew up in a Pittsburgh community that was rich in jazz history. His neighbors included the legendary pianists Earl Hines, Errol Garner and Mary Lou Williams. As a youth, Jamal delivered newspapers to the household of Billy Strayhorn. When Jamal began his professional career at the age of 14, Art Tatum, an early titan of the keyboard, proclaimed him "a coming great." During a tour stop in Detroit, Jamal, who was born to Baptist parents, converted to Islam and changed his name.</p>
</article></body></html>"""


def test_save_article(test_client, user):
    readable = "This is a test summary"
    readable_bytes = readable.encode('utf-8')
    readable_gzipped = gzip.compress(readable_bytes)
    readable_gzipped_b64 = base64.b64encode(readable_gzipped).decode('utf-8')

    html_bytes = html.encode('utf-8')
    html_gzipped = gzip.compress(html_bytes)
    html_gzipped_b64 = base64.b64encode(
        html_gzipped).decode('utf-8')

    data = {"document": html_gzipped_b64,
            "readable": readable_gzipped_b64,
            "title": "Test Title",
            "url": "https://example.com/article"}

    headers = {'Content-Type': 'application/json'}

    # Test valid article
    response = test_client.post(
        '/api/articles', data=json.dumps(data), headers=headers)
    assert response.status_code == 200
    response_json = json.loads(response.data)
    assert response_json['blurb'] == "This is a test summary"
    assert response_json['content'].startswith(readable)
    assert response_json['url'] == "https://example.com/article"
    assert response_json['type'] == "external"
    # Checking if the user is associated with the post
    post = Post.query.filter_by(url="https://example.com/article").first()
    assert post is not None
    assert user in post.users


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
