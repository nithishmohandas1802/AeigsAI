from app.models.user import User
from app.security.password import hash_password
from app.security.jwt import create_access_token, decode_access_token
from datetime import datetime, timedelta, timezone

import jwt

from app.config.settings import settings

def test_login_with_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "doesnotexist@example.com",
            "password": "wrongpassword123",
        },
    )

    assert response.status_code == 401


def test_login_with_valid_credentials(client, db):
    test_user = User(
        username="testuser",
        email="testuser@example.com",
        password_hash=hash_password("password123"),
    )

    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    response = client.post(
        "/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_login_with_missing_email(client):
    response = client.post(
        "/auth/login",
        json={
            "password": "password123",
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["message"] == "Request validation failed"
    assert data["error"]["status"] == 422
    assert data["error"]["details"]


def test_login_with_invalid_email(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "not-an-email",
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_login_with_missing_password(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
        },
    )

    assert response.status_code == 422


def test_login_with_short_password(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422

def test_access_protected_endpoint_with_valid_token(client, db):
    test_user = User(
        username="protecteduser",
        email="protected@example.com",
        password_hash=hash_password("password123"),
    )

    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    token = create_access_token(
        {
            "sub": str(test_user.id),
            "email": test_user.email,
        }
    )

    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

def test_access_protected_endpoint_without_token(client):
    response = client.get("/users/")

    assert response.status_code == 401

def test_access_protected_endpoint_with_invalid_token(client):
    response = client.get(
        "/users/",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401

def test_access_protected_endpoint_with_nonexistent_user_token(client):
    token = create_access_token(
        {
            "sub": "999999",
            "email": "ghost@example.com",
        }
    )

    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401

def test_user_cannot_update_another_user(client, db):
    user_one = User(
        username="userone",
        email="userone@example.com",
        password_hash=hash_password("password123"),
    )

    user_two = User(
        username="usertwo",
        email="usertwo@example.com",
        password_hash=hash_password("password123"),
    )

    db.add_all([user_one, user_two])
    db.commit()

    db.refresh(user_one)
    db.refresh(user_two)

    token = create_access_token(
        {
            "sub": str(user_one.id),
            "email": user_one.email,
        }
    )

    response = client.put(
        f"/users/{user_two.id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "username": "hackeduser",
            "email": "hacked@example.com",
        },
    )

    assert response.status_code == 403

def test_user_cannot_patch_another_user(client, db):
    user_one = User(
        username="patchuserone",
        email="patchuserone@example.com",
        password_hash=hash_password("password123"),
    )

    user_two = User(
        username="patchusertwo",
        email="patchusertwo@example.com",
        password_hash=hash_password("password123"),
    )

    db.add_all([user_one, user_two])
    db.commit()

    db.refresh(user_one)
    db.refresh(user_two)

    token = create_access_token(
        {
            "sub": str(user_one.id),
            "email": user_one.email,
        }
    )

    response = client.patch(
        f"/users/{user_two.id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "username": "hackedpatchuser",
        },
    )

    assert response.status_code == 403

def test_user_cannot_delete_another_user(client, db):
    user_one = User(
        username="deleteuserone",
        email="deleteuserone@example.com",
        password_hash=hash_password("password123"),
    )

    user_two = User(
        username="deleteusertwo",
        email="deleteusertwo@example.com",
        password_hash=hash_password("password123"),
    )

    db.add_all([user_one, user_two])
    db.commit()

    db.refresh(user_one)
    db.refresh(user_two)

    token = create_access_token(
        {
            "sub": str(user_one.id),
            "email": user_one.email,
        }
    )

    response = client.delete(
        f"/users/{user_two.id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403

def test_login_returns_valid_jwt(client, db):
    test_user = User(
        username="jwtuser",
        email="jwtuser@example.com",
        password_hash=hash_password("password123"),
    )

    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    response = client.post(
        "/auth/login",
        json={
            "email": "jwtuser@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    access_token = data["access_token"]

    payload = decode_access_token(access_token)

    assert payload["sub"] == str(test_user.id)
    assert payload["email"] == test_user.email

def test_access_protected_endpoint_with_malformed_token(client):
    response = client.get(
        "/users/",
        headers={
            "Authorization": "Bearer this-is-not-a-valid-jwt",
        },
    )

    assert response.status_code == 401

def test_access_protected_endpoint_with_expired_token(client):
    expired_token = jwt.encode(
        {
            "sub": "1",
            "email": "expired@example.com",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {expired_token}",
        },
    )

    assert response.status_code == 401

def test_access_protected_endpoint_with_token_without_sub(client):
    token = create_access_token(
        {
            "email": "nosub@example.com",
        }
    )

    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401

def test_unauthorized_error_response(client):
    response = client.get(
        "/users/",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "HTTP_ERROR"
    assert data["error"]["message"] == "Invalid or expired token"
    assert data["error"]["status"] == 401

def test_missing_authentication_error_response(client):
    response = client.get("/users/")

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "HTTP_ERROR"
    assert data["error"]["status"] == 401

def test_forbidden_error_response(client, db):
    user_one = User(
        username="forbiddenone",
        email="forbiddenone@example.com",
        password_hash=hash_password("password123"),
    )

    user_two = User(
        username="forbiddentwo",
        email="forbiddentwo@example.com",
        password_hash=hash_password("password123"),
    )

    db.add_all([user_one, user_two])
    db.commit()

    db.refresh(user_one)
    db.refresh(user_two)

    token = create_access_token(
        {
            "sub": str(user_one.id),
            "email": user_one.email,
        }
    )

    response = client.put(
        f"/users/{user_two.id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "username": "hackeduser",
            "email": "hacked@example.com",
        },
    )

    assert response.status_code == 403

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "FORBIDDEN"
    assert data["error"]["message"] == (
    "You are not allowed to update this user"
)
    assert data["error"]["status"] == 403

def test_validation_error_response(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "not-an-email",
            "password": "short",
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["message"] == "Request validation failed"
    assert data["error"]["status"] == 422
    assert isinstance(data["error"]["details"], list)
    assert len(data["error"]["details"]) >= 1
