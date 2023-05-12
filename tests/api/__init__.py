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


def create_post(user=None, type='public', **kwargs):
    if not user:
        user = get_or_create_user()

    post = Post(type=type, **kwargs)

    user.posts.append(post)

    db.session.add(post)
    db.session.commit()
    return post
