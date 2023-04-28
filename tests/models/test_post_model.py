from datetime import datetime
from spyglasses.models import Post, db
from tests.api import create_post


def test_check_post_exists(test_client):
    # Create a post with unique content and URL
    post1 = create_post(content="Content 1",
                        url="https://example.com/article1")
    assert post1 is not None

    # Attempt to create another post with the same content
    post2 = create_post(content="Content 1",
                        url="https://example.com/article2")
    assert len(Post.query.all()) == 1

    # Attempt to create another post with the same URL
    post3 = create_post(content="Content 2",
                        url="https://example.com/article1")
    assert len(Post.query.all()) == 1

    # Attempt to create another post with the same content and URL
    post4 = create_post(content="Content 1",
                        url="https://example.com/article1")
    assert len(Post.query.all()) == 1

    # Attempt to create another post with different content and URL
    post5 = create_post(content="Content 3",
                        url="https://example.com/article3")
    assert len(Post.query.all()) == 2

    # Check that the existing post is not updated
    existing_post = Post.query.filter_by(id=post1.id).first()
    assert existing_post.content == "Content 1"
    assert existing_post.url == "https://example.com/article1"


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
