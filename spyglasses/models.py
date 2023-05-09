import hashlib
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import event, or_, and_
from sqlalchemy.orm import object_session

db = SQLAlchemy()


class User(db.Model, SerializerMixin):
    serialize_only = ('id', 'auth_user_id', 'email',
                      'given_name', 'family_name')
    email = db.Column(db.String(120), unique=True, nullable=False)
    given_name = db.Column(db.String(120), nullable=True)
    family_name = db.Column(db.String(120), nullable=True)
    id = db.Column(db.Integer, primary_key=True)
    auth_user_id = db.Column(db.String(64), unique=True, nullable=False)
    posts = db.relationship('Post', backref='user', lazy=True)


class Post(db.Model, SerializerMixin):
    serialize_only = ('id', 'title', 'blurb', 'created_at', 'user.id',
                      'url', 'type', 'updated_at', 'content', 'notes.id', 'highlights.id')
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=True)
    blurb = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)
    document = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)
    highlights = db.relationship('Highlight', backref='post', lazy=True)
    notes = db.relationship('Note', backref='post', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_hash = db.Column(db.String(64), nullable=False, unique=True)
    url = db.Column(db.String(2048), nullable=True, unique=True)
    type = db.Column(db.Enum('public', 'private', 'external',
                     name="PostTypes"), nullable=False)


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


def find_post(content, user_id, url=None):
    """
    Find or create a Post instance with the given content, user_id, and url.
    """
    content_hash = generate_hash(content)
    if url:
        existing_post = db.session.query(Post).filter(
            and_(
                Post.user_id == user_id,
                or_(
                    Post.content_hash == content_hash,
                    Post.url == url
                )
            )
        ).first()
    else:
        existing_post = db.session.query(Post).filter(
            and_(
                Post.user_id == user_id,
                Post.content_hash == content_hash
            )
        ).first()

    return existing_post
