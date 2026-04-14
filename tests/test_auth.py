import pytest
from security import get_password_hash
from models import User


def create_test_user(db_session):
    """Helper to create a test user. Deletes any existing one first to avoid unique constraint errors."""
    # Clean up any previous test user
    db_session.query(User).filter(User.email == "test@example.com").delete()
    db_session.commit()

    hashed = get_password_hash("testpassword123")
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed,
        is_active=1,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_login_success(client, db_session):
    """POST /auth/token with correct credentials → returns token"""
    create_test_user(db_session)

    response = client.post(
        "/auth/token",
        data={
            "username": "testuser",
            "password": "testpassword123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, db_session):
    """Wrong password → should return 401"""
    create_test_user(db_session)

    response = client.post(
        "/auth/token",
        data={
            "username": "testuser",
            "password": "wrongpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Non-existent user → should return 401"""
    response = client.post(
        "/auth/token",
        data={
            "username": "nonexistentuser",
            "password": "anypassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 401