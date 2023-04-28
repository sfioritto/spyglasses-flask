from flask import jsonify, request, Blueprint
from spyglasses.models import Post, db

bp = Blueprint("v1", __name__)


def json_for_post(post):
    return jsonify({
        'id': post.id,
        'blurb': post.blurb,
        'content': post.content,
        'post_type': post.post_type,
        'created_at': post.created_at,
        'updated_at': post.updated_at,
    })


@bp.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    post_list = []

    for post in posts:
        post_data = {
            'id': post.id,
            'blurb': post.blurb,
            'post_type': post.post_type,
            'created_at': post.created_at,
            'updated_at': post.updated_at,
        }
        post_list.append(post_data)

    return jsonify(post_list)


@bp.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    if not data or 'content' not in data or 'post_type' not in data:
        return jsonify({"error": "Missing content or post_type in request data"}), 400

    post = Post(content=data['content'], post_type=data['post_type'])

    if 'blurb' in data:
        post.blurb = data['blurb']

    db.session.add(post)
    db.session.commit()

    return jsonify({"message": "Post created successfully", "post_id": post.id}), 201


@bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return json_for_post(post)


@bp.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    data = request.get_json()

    if "blurb" in data:
        post.blurb = data["blurb"]
    if "content" in data:
        post.content = data["content"]
    if "post_type" in data:
        post.post_type = data["post_type"]

    db.session.commit()

    return json_for_post(post)


@bp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    # Code for deleting a specific post
    pass


@bp.route('/posts/<int:post_id>/notes', methods=['GET'])
def get_notes(post_id):
    # Code for getting notes of a specific post
    pass


@bp.route('/posts/<int:post_id>/notes', methods=['POST'])
def create_note(post_id):
    # Code for creating a new note for a specific post
    pass
