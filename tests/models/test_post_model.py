from datetime import datetime
from spyglasses.models import Post, db


def test_check_content_hash_exists(test_client):
    """
    Test that the content hash is created and checked
    note: have to include test_client otherwise the test
    app will not be created
    """
    # Create the first post
    post1 = Post(
        blurb='Test Title 1',
        content='Test Content 1',
        type='external',
        created_at=datetime.utcnow(),
        user_id=1,
    )
    db.session.add(post1)
    db.session.commit()

    # Create a duplicate post
    post2 = Post(
        blurb='Test Title 2',
        content='Test Content 1',
        type='external',
        created_at=datetime.utcnow(),
        user_id=1,
    )
    db.session.add(post2)
    db.session.commit()

    # Verify that only one post exists with the same content hash
    posts = Post.query.all()
    assert len(posts) == 1

    # Verify that the first post was not overwritten by the second post
    assert posts[0].blurb == 'Test Title 1'
    assert posts[0].content == 'Test Content 1'
