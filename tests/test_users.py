from app.models.user import User
from app.security.jwt import create_access_token
from app.security.password import hash_password


def create_test_user(db, username="testuser", email="test@example.com"):
    user = User(
        username=username,
        email=email,
        password_hash=hash_password("password123"),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_auth_headers(user):
    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
        }
    )

    return {
        "Authorization": f"Bearer {token}",
    }


def test_create_user(client):
    response = client.post(
        "/users",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"]
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "password" not in data
    assert "password_hash" not in data


def test_create_duplicate_username(client, db):
    create_test_user(
        db,
        username="duplicateuser",
        email="first@example.com",
    )

    response = client.post(
        "/users",
        json={
            "username": "duplicateuser",
            "email": "second@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 409


def test_create_duplicate_email(client, db):
    create_test_user(
        db,
        username="firstuser",
        email="duplicate@example.com",
    )

    response = client.post(
        "/users",
        json={
            "username": "seconduser",
            "email": "duplicate@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 409


def test_get_user_by_id(client, db):
    user = create_test_user(db)

    response = client.get(
        f"/users/{user.id}",
        headers=get_auth_headers(user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user.id
    assert data["username"] == user.username
    assert data["email"] == user.email


def test_get_nonexistent_user(client, db):
    user = create_test_user(db)

    response = client.get(
        "/users/999999",
        headers=get_auth_headers(user),
    )

    assert response.status_code == 404


def test_update_user(client, db):
    user = create_test_user(db)

    response = client.put(
        f"/users/{user.id}",
        headers=get_auth_headers(user),
        json={
            "username": "updateduser",
            "email": "updated@example.com",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "updateduser"
    assert data["email"] == "updated@example.com"


def test_patch_user(client, db):
    user = create_test_user(db)

    response = client.patch(
        f"/users/{user.id}",
        headers=get_auth_headers(user),
        json={
            "username": "patcheduser",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "patcheduser"
    assert data["email"] == user.email


def test_patch_user_requires_field(client, db):
    user = create_test_user(db)

    response = client.patch(
        f"/users/{user.id}",
        headers=get_auth_headers(user),
        json={},
    )

    assert response.status_code == 422

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_delete_user(client, db):
    user = create_test_user(db)

    response = client.delete(
        f"/users/{user.id}",
        headers=get_auth_headers(user),
    )

    assert response.status_code == 204

    deleted_user = (
        db.query(User)
        .filter(User.id == user.id)
        .first()
    )

    assert deleted_user is None

def test_get_user_without_token(client, db):
    user = create_test_user(db)

    response = client.get(
        f"/users/{user.id}",
    )

    assert response.status_code == 401
