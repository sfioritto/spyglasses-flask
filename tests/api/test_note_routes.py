from spyglasses.models import Post, User, Note, db


def test_get_notes(test_client, user):
    post = Post(user=user, content="Test content", post_type="text")
    note1 = Note(content="Note 1", post=post)
    note2 = Note(content="Note 2", post=post)
    db.session.add_all([user, post, note1, note2])
    db.session.commit()

    # Send a GET request to the route
    response = test_client.get(f'/api/posts/{post.id}/notes')

    # Check if the response is successful and the notes are returned
    assert response.status_code == 200
    assert response.json == [note1.to_dict(), note2.to_dict()]


def test_create_note(test_client):
    # Create a test user and post, and add them to the database
    user = User(username="testuser", password="testpassword")
    post = Post(user=user, content="Test content", post_type="text")
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
