import pytest
from models import User, Comment, ArtImage

def create_test_user_and_image(db_session):
    """Helper: clean + create test user + image with FIXED ID matching the mock"""
    # Clean previous data
    db_session.query(Comment).delete()
    db_session.query(ArtImage).delete()
    db_session.query(User).filter(User.email == "test@example.com").delete()
    db_session.commit()

    # Create user with ID=999 to match the mocked current_user in conftest.py
    user = User(
        id=999,                          # ← important
        username="testuser",
        email="test@example.com",
        hashed_password="dummy",
        is_active=1,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    image = ArtImage(
        title="Test Nail Art",
        image_url="/static/images/test.jpg",
        artist="Nails by Mykala"
    )
    db_session.add(image)
    db_session.commit()
    db_session.refresh(image)

    return user, image


def test_create_comment(client, db_session):
    """POST /comments/ should create a comment"""
    _, image = create_test_user_and_image(db_session)

    response = client.post(
        "/comments/",
        json={"text": "This nail art is fire! 🔥", "image_id": image.id}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "This nail art is fire! 🔥"
    assert data["username"] == "testuser"


def test_get_comments_for_image(client, db_session):
    """GET /comments/image/{id} should return list of comments"""
    user, image = create_test_user_and_image(db_session)

    comment = Comment(text="Looks amazing!", image_id=image.id, user_id=user.id)
    db_session.add(comment)
    db_session.commit()

    response = client.get(f"/comments/image/{image.id}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_update_own_comment(client, db_session):
    """PUT /comments/{id} should allow owner to edit"""
    user, image = create_test_user_and_image(db_session)
    comment = Comment(text="Old comment", image_id=image.id, user_id=user.id)
    db_session.add(comment)
    db_session.commit()
    db_session.refresh(comment)

    response = client.put(
        f"/comments/{comment.id}",
        json={"text": "Updated comment - even better now!"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Updated comment - even better now!"


def test_delete_own_comment(client, db_session):
    """DELETE /comments/{id} should allow owner to delete"""
    user, image = create_test_user_and_image(db_session)
    comment = Comment(text="To be deleted", image_id=image.id, user_id=user.id)
    db_session.add(comment)
    db_session.commit()
    db_session.refresh(comment)

    response = client.delete(f"/comments/{comment.id}")

    assert response.status_code == 204