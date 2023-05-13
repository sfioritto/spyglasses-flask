from spyglasses.models import Post, User, Note, db
from tests.api import get_or_create_user


def test_get_notes(test_client, user):
    second_user = get_or_create_user(auth_user_id="second_user")

    post = Post(content="Test content", type="public")
    post.users.append(user)
    post.users.append(second_user)
    note1 = Note(content="Note 1", post=post, user_id=user.id)
    note2 = Note(content="Note 2", post=post, user_id=user.id)
    note3 = Note(content="Note 3", post=post, user_id=second_user.id)
    db.session.add_all([user, post, note1, note2, note3])
    db.session.commit()

    response = test_client.get(f'/api/posts/{post.id}/notes')

    # Check if the response is successful and the notes are returned
    assert response.status_code == 200
    assert response.json == [note1.to_dict(), note2.to_dict()]


def test_create_note(test_client, user):
    post = Post(content="Test content", type="public")
    post.users.append(user)
    db.session.add_all([user, post])
    db.session.commit()

    # Send a POST request to the route with note content
    new_note_data = {"content": "New note"}
    response = test_client.post(
        f'/api/posts/{post.id}/notes', json=new_note_data)

    # Check if the response is successful and the note is created
    assert response.status_code == 201
    assert response.json["message"] == "Note created successfully"
    assert "note_id" in response.json

    # Verify the new note is in the database
    created_note = Note.query.get(response.json["note_id"])
    assert created_note is not None
    assert created_note.content == new_note_data["content"]
    assert created_note.post_id == post.id
    assert created_note.user_id == user.id
