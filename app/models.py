from datetime import datetime
from app import db


class Post(db.Model):
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


class Highlight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_pos = db.Column(db.Integer, nullable=False)
    end_pos = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    notes = db.relationship('Note', backref='highlight', lazy=True)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    highlight_id = db.Column(
        db.Integer, db.ForeignKey('highlight.id'), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
