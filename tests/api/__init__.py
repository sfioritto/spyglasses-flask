from spyglasses.models import Post, db, User


def get_or_create_user(auth_user_id='dev'):
    user = User.query.filter_by(auth_user_id='dev').first()

    # If the dev user does not exist, create one
    if user is None:
        user = User(
            given_name=auth_user_id,
            family_name='developer',
            email=f'{auth_user_id}@test.com',
            auth_user_id=auth_user_id,
        )
        db.session.add(user)
        db.session.commit()

    return user


def create_post(**kwargs):
    if 'user' not in kwargs:
        kwargs['user'] = get_or_create_user()
    if 'type' not in kwargs:
        kwargs['type'] = 'public'
    post = Post(**kwargs)
    db.session.add(post)
    db.session.commit()
    return post
