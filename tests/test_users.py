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


def test_get_nonexistent_user_returns_standard_error(client, db):
    user = create_test_user(db)

    response = client.get(
        "/users/999999",
        headers=get_auth_headers(user),
    )

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "USER_NOT_FOUND"
    assert data["error"]["message"] == "User not found"
    assert data["error"]["status"] == 404


def test_user_cannot_update_another_user_returns_standard_error(
    client,
    db,
):
    user = create_test_user(
        db,
        username="userone",
        email="userone@example.com",
    )

    another_user = create_test_user(
        db,
        username="usertwo",
        email="usertwo@example.com",
    )

    response = client.put(
        f"/users/{another_user.id}",
        headers=get_auth_headers(user),
        json={
            "username": "updateduser",
            "email": "updated@example.com",
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


# ============================================================
# Build 022 — Pagination and Filtering Tests
# ============================================================


def test_get_users_default_pagination(client, db):
    current_user = create_test_user(
        db,
        username="paginationuser",
        email="pagination@example.com",
    )

    for index in range(12):
        create_test_user(
            db,
            username=f"user{index}",
            email=f"user{index}@example.com",
        )

    response = client.get(
        "/users/",
        headers=get_auth_headers(current_user),
    )

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert data["total"] == 13
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["pages"] == 2
    assert len(data["items"]) == 10


def test_get_users_second_page(client, db):
    current_user = create_test_user(
        db,
        username="pageuser",
        email="page@example.com",
    )

    for index in range(12):
        create_test_user(
            db,
            username=f"pageuser{index}",
            email=f"pageuser{index}@example.com",
        )

    response = client.get(
        "/users/?page=2&page_size=5",
        headers=get_auth_headers(current_user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 13
    assert data["page"] == 2
    assert data["page_size"] == 5
    assert data["pages"] == 3
    assert len(data["items"]) == 5


def test_get_users_last_page_returns_remaining_items(client, db):
    current_user = create_test_user(
        db,
        username="lastpageuser",
        email="lastpage@example.com",
    )

    for index in range(7):
        create_test_user(
            db,
            username=f"lastuser{index}",
            email=f"lastuser{index}@example.com",
        )

    response = client.get(
        "/users/?page=2&page_size=5",
        headers=get_auth_headers(current_user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 8
    assert data["page"] == 2
    assert data["page_size"] == 5
    assert data["pages"] == 2
    assert len(data["items"]) == 3


def test_get_users_filters_by_username(client, db):
    current_user = create_test_user(
        db,
        username="filtercurrent",
        email="filtercurrent@example.com",
    )

    create_test_user(
        db,
        username="alice",
        email="alice@example.com",
    )

    create_test_user(
        db,
        username="bob",
        email="bob@example.com",
    )

    response = client.get(
        "/users/?username=alice",
        headers=get_auth_headers(current_user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["pages"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["username"] == "alice"


def test_get_users_filters_by_email(client, db):
    current_user = create_test_user(
        db,
        username="emailfiltercurrent",
        email="emailfiltercurrent@example.com",
    )

    create_test_user(
        db,
        username="alice",
        email="alice@example.com",
    )

    create_test_user(
        db,
        username="bob",
        email="bob@example.com",
    )

    response = client.get(
        "/users/?email=alice@example.com",
        headers=get_auth_headers(current_user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["email"] == "alice@example.com"


def test_get_users_filter_and_pagination(client, db):
    current_user = create_test_user(
        db,
        username="combinedcurrent",
        email="combinedcurrent@example.com",
    )

    for index in range(6):
        create_test_user(
            db,
            username=f"team{index}",
            email=f"team{index}@example.com",
        )

    create_test_user(
        db,
        username="other",
        email="other@example.com",
    )

    response = client.get(
        "/users/?username=team3&page=1&page_size=2",
        headers=get_auth_headers(current_user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["pages"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["username"] == "team3"


def test_get_users_filter_returns_empty_result(client, db):
    current_user = create_test_user(
        db,
        username="emptyfilter",
        email="emptyfilter@example.com",
    )

    response = client.get(
        "/users/?username=does-not-exist",
        headers=get_auth_headers(current_user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["pages"] == 0


def test_get_users_rejects_invalid_page(client, db):
    current_user = create_test_user(
        db,
        username="invalidpage",
        email="invalidpage@example.com",
    )

    response = client.get(
        "/users/?page=0",
        headers=get_auth_headers(current_user),
    )

    assert response.status_code == 422

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_get_users_rejects_negative_page(client, db):
    current_user = create_test_user(
        db,
        username="negativepage",
        email="negativepage@example.com",
    )

    response = client.get(
        "/users/?page=-1",
        headers=get_auth_headers(current_user),
    )

    assert response.status_code == 422


def test_get_users_rejects_zero_page_size(client, db):
    current_user = create_test_user(
        db,
        username="zeropagesize",
        email="zeropagesize@example.com",
    )

    response = client.get(
        "/users/?page_size=0",
        headers=get_auth_headers(current_user),
    )

    assert response.status_code == 422


def test_get_users_rejects_page_size_above_maximum(client, db):
    current_user = create_test_user(
        db,
        username="largepagesize",
        email="largepagesize@example.com",
    )

    response = client.get(
        "/users/?page_size=101",
        headers=get_auth_headers(current_user),
    )

    assert response.status_code == 422


def test_get_users_without_token_returns_401(client):
    response = client.get("/users/")

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "UNAUTHORIZED"