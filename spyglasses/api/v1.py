import gzip
import base64
import json
from io import BytesIO
from flask import g, jsonify, request, Blueprint
from html2text import html2text
from newspaper import Article
from spyglasses.models import Post, Note, db
from spyglasses.views import load_user

API_VERSION = "v1"
bp = Blueprint(API_VERSION, __name__)

bp.before_request(load_user)


@bp.route('/articles', methods=['POST'])
def save_article():
    request_data = json.loads(request.data)

    gzipped_document = base64.b64decode(request_data['document'])
    with gzip.open(BytesIO(gzipped_document), 'rt', encoding='utf-8') as f:
        document = f.read()

    url = request_data['url']

    # Parse the article using newspaper3k
    article = Article('')
    article.set_html(document)
    article.parse()
    if article.is_valid_body():
        markdown_content = html2text(article.text)
        # Create a new Post instance with the parsed data
        post = Post(
            blurb=article.title,
            content=markdown_content,
            type='external',
            document=document,
            url=url,
            user=g.user,
            title=article.title,
        )

        # Save the Post instance to the database
        db.session.add(post)
        db.session.commit()

        # Return the saved Post data as JSON
        return jsonify(post.to_dict())
    else:
        return jsonify({"error": "Not an article"}), 400


@bp.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    post_list = []

    for post in posts:
        post_data = post.to_dict()
        del post_data['content']
        post_list.append(post_data)

    return jsonify(post_list)


@bp.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    if not data or 'content' not in data or 'type' not in data:
        return jsonify({"error": "Missing content or type in request data"}), 400

    kwargs = {**data, 'user_id': g.user.id}
    post = Post(**kwargs)

    if 'blurb' in data:
        post.blurb = data['blurb']

    db.session.add(post)
    db.session.commit()

    return jsonify({"message": "Post created successfully", "post_id": post.id}), 201


@bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_dict())


@bp.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    data = request.get_json()

    if "blurb" in data:
        post.blurb = data["blurb"]
    if "content" in data:
        post.content = data["content"]
    if "type" in data:
        post.type = data["type"]

    db.session.commit()

    serialized_post = post.to_dict()
    serialized_post['content'] = post.content
    return jsonify(serialized_post)


@bp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Post deleted"})


@bp.route('/posts/<int:post_id>/notes', methods=['GET'])
def get_notes(post_id):
    post = Post.query.get_or_404(post_id)
    notes = [note.to_dict() for note in post.notes]
    return jsonify(notes)


@bp.route('/posts/<int:post_id>/notes', methods=['POST'])
def create_note(post_id):
    post = Post.query.get_or_404(post_id)
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"error": "Missing content in request data"}), 400

    note = Note(content=data['content'], post_id=post.id)
    db.session.add(note)
    db.session.commit()

    return jsonify({"message": "Note created successfully", "note_id": note.id}), 201
