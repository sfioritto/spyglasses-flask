import hashlib
from datetime import datetime
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import event
from sqlalchemy.orm import object_session
db = SQLAlchemy()


class User(db.Model, SerializerMixin):
    serialize_only = ('id', 'username')
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    posts = db.relationship('Post', backref='user', lazy=True)


class Post(db.Model, SerializerMixin):
    serialize_only = ('id', 'blurb', 'content',
                      'post_type', 'created_at', 'user.id')
    id = db.Column(db.Integer, primary_key=True)
    blurb = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)
    post_type = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)
    highlights = db.relationship('Highlight', backref='post', lazy=True)
    notes = db.relationship('Note', backref='post', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_hash = db.Column(db.String(64), nullable=False, unique=True)


class Highlight(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    start_pos = db.Column(db.Integer, nullable=False)
    end_pos = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    notes = db.relationship('Note', backref='highlight', lazy=True)


class Note(db.Model, SerializerMixin):
    serialize_rules = ('-highlight', '-post')
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    highlight_id = db.Column(
        db.Integer, db.ForeignKey('highlight.id'), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)


def generate_hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


@event.listens_for(Post.content, 'set')
def update_content_hash(target, value, *args):
    """
    Update the content_hash property whenever the content property is set.
    """
    target.content_hash = generate_hash(value)

    # Flush the session to make the changes persistent
    session = object_session(target)
    if session:
        session.flush()


@event.listens_for(db.session, 'before_flush')
def check_content_hash_exists(session, flush_context, instances):
    """
    Check if the content_hash column already exists before creating a new Post instance.
    If it exists, update the existing post instead of creating a new one.
    """
    for target in session.new:
        if not isinstance(target, Post):
            continue

        # Check if a Post instance with the same content_hash already exists in the database
        content_hash = generate_hash(target.content)
        existing_post = session.query(Post).filter_by(
            content_hash=content_hash).first()

        # If a Post instance with the same content_hash already exists, update it
        if existing_post:
            # Remove the new object from the session to prevent it from being inserted
            session.expunge(target)
        else:
            # If no existing post, set the content_hash for the new post
            target.content_hash = content_hash
