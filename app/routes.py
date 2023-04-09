from flask import request, jsonify
from app import app, db
from app.models import Post, Note


@app.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return jsonify([post.to_dict() for post in posts])


@app.route('/posts', methods=['POST'])
def create_post():
    # Code for creating a new post
    pass


@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    # Code for getting a specific post
    pass


@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    # Code for updating a specific post
    pass


@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    # Code for deleting a specific post
    pass


@app.route('/posts/<int:post_id>/notes', methods=['GET'])
def get_notes(post_id):
    # Code for getting notes of a specific post
    pass


@app.route('/posts/<int:post_id>/notes', methods=['POST'])
def create_note(post_id):
    # Code for creating a new note for a specific post
    pass
