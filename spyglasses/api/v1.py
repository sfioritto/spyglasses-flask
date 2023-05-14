import gzip
import base64
import json
from io import BytesIO
from flask import g, jsonify, request, Blueprint
from spyglasses.models import Post, Note, db, find_post, user_post_association
from spyglasses.views import load_user
from spyglasses import ai
from markdownify import markdownify as md
from sqlalchemy import and_


API_VERSION = "v1"
bp = Blueprint(API_VERSION, __name__)

bp.before_request(load_user)


@bp.route('/articles', methods=['POST'])
async def save_article():
    request_data = json.loads(request.data)

    gzipped_document = base64.b64decode(request_data['document'])
    with gzip.open(BytesIO(gzipped_document), 'rt', encoding='utf-8') as f:
        document = f.read()

    gzipped_readable = base64.b64decode(request_data['readable'])
    with gzip.open(BytesIO(gzipped_readable), 'rt', encoding='utf-8') as f:
        readable = f.read()

    title = request_data['title']
    url = request_data['url']

    if not ai.is_article(document):
        return jsonify({
            'message': 'Not an article'
        }), 400

    markdown = md(readable)
    post = find_post(markdown, url)
    if not post:
        summary = await ai.summarize(markdown)
        post = Post(
            content=markdown,
            summary=summary,
            type='external',
            document=document,
            url=url,
            title=title,
        )
        db.session.add(post)
    # Check if the user is already associated with the post
    user_has_post = db.session.query(user_post_association).filter(
        and_(
            user_post_association.c.user_id == g.user.id,
            user_post_association.c.post_id == post.id
        )
    ).one_or_none()

    if not user_has_post:
        association = user_post_association.insert().values(
            user_id=g.user.id, post_id=post.id)
        db.session.execute(association)

    db.session.commit()

    return jsonify(post.to_dict())


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

    post = Post(content=data['content'], type=data['type'])

    g.user.posts.append(post)

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

    if "summary" in data:
        post.summary = data["summary"]
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
    notes = Note.query.filter_by(post_id=post.id, user_id=g.user.id).all()
    notes_dicts = [note.to_dict() for note in notes]
    return jsonify(notes_dicts)


@bp.route('/posts/<int:post_id>/notes', methods=['POST'])
def create_note(post_id):
    post = Post.query.get_or_404(post_id)
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"error": "Missing content in request data"}), 400

    note = Note(content=data['content'], post_id=post.id, user_id=g.user.id)
    db.session.add(note)
    db.session.commit()

    return jsonify({"message": "Note created successfully", "note_id": note.id}), 201
