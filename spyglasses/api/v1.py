from functools import wraps
from flask_jwt_extended import jwt_required
from flask import g, jsonify, request, Blueprint, current_app
from flask_jwt_extended import create_access_token, verify_jwt_in_request, get_jwt_identity
from spyglasses.models import Post, Note, User, db
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint("v1", __name__)


def jwt_exempt(f):
    f._jwt_exempt = True
    return f


@bp.before_request
def load_current_user():
    try:
        # Check if JWT exists and is valid
        verify_jwt_in_request()
        # Get the current user's identity
        current_user_identity = get_jwt_identity()
        # Fetch the user from your database, e.g., using user ID or username
        # Replace 'User' with your user model
        current_user = User.query.get(current_user_identity)
        # Store the user in the 'g' object
        g.user = current_user
    except Exception as e:
        # If there's no JWT or it's invalid, set current_user to None
        g.user = None


@bp.before_request
def require_jwt_for_all_routes():
    # Get the current route function
    route_func = current_app.view_functions.get(request.endpoint)

    if route_func and not getattr(route_func, '_jwt_exempt', False):
        @wraps(require_jwt_for_all_routes)
        def wrapper():
            pass

        jwt_required()(wrapper)()


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
    if "post_type" in data:
        post.post_type = data["post_type"]

    db.session.commit()

    return jsonify(post.to_dict())


@ bp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Post deleted"})


@ bp.route('/posts/<int:post_id>/notes', methods=['GET'])
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


@bp.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({"msg": "Username already exists"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.to_dict()), 201


@bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_dict()), 200


@bp.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({"error": "Nothing to update"}), 400

    if username:
        user.username = username

    db.session.commit()

    return jsonify(user.to_dict()), 200


@bp.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"result": "User deleted"}), 200


@jwt_exempt
@bp.route('/login', methods=['POST'])
def create_token():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid username or password"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token}), 200
