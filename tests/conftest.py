import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
from models import User, ArtImage, Comment
from security import get_current_user, get_current_admin

# Shared in-memory database for all tests
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# Regular user client (for images/comments/auth tests)
@pytest.fixture(scope="function")
def client(db_session):
    test_user = User(id=999, username="testuser", email="test@example.com",
                     hashed_password="dummy", is_active=1, is_admin=False)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# Admin client (for admin-only routes)
@pytest.fixture(scope="function")
def admin_client(db_session):
    admin_user = User(id=9999, username="adminuser", email="admin@example.com",
                      hashed_password="dummy", is_active=1, is_admin=True)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_admin():
        return admin_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_admin] = override_get_current_admin

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()