import pytest
from spyglasses.models import db
from tests.api import get_or_create_user, create_post


def set_user_session(test_client, user):
    with test_client.session_transaction() as session:
        session["user"] = {
            "sub": user.auth_user_id,
            "email": user.email,
            "given_name": user.given_name,
            "family_name": user.family_name,
        }


@pytest.fixture(autouse=True)
def user():
    user = get_or_create_user()
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(autouse=True)
def auto_set_user_session(request, test_client):
    # Check if the test function uses the 'user' fixture
    if "user" in request.fixturenames:
        set_user_session(test_client, request.getfixturevalue("user"))
