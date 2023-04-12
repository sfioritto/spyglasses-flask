from spyglasses.models import User, Post, db


def get_or_create_user(username="user1"):
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username=username, password="password")
        db.session.add(user)
        db.session.commit()
    return user


def create_post(**kwargs):
    if 'user' not in kwargs:
        kwargs['user'] = get_or_create_user()
    post = Post(**kwargs)
    print(post.to_dict())
    db.session.add(post)
    db.session.commit()
    return post
