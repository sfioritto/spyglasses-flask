import hashlib
from datetime import datetime
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


@event.listens_for(Post.content, 'set')
def update_content_hash(target, value, *args):
    """
    Update the content_hash property whenever the content property is set.
    """
    # Create a hash of the parsed article text
    content_hash = hashlib.sha256(value.encode('utf-8')).hexdigest()
    target.content_hash = content_hash

    # Flush the session to make the changes persistent
    session = object_session(target)
    if session:
        session.flush()
