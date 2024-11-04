"""
TODO: Нужно отрефакторить, сделано сильно на скорую руку

"""
import os

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.__main__ import app
from src.config.database import engine
from src.interfaces.protocols import PasswordHasherProtocol
from src.services.user_service import UserService

URL = "http://127.0.0.1:8000"
TEST_DIR = os.path.dirname(__file__)
GOOD_IMAGE_PATH = os.path.join(TEST_DIR, "files/ava.jpg")
BAD_IMAGE_PATH = os.path.join(TEST_DIR, "files/ava.txt")


@pytest.mark.asyncio
async def test_nonexistent_page():
    async with AsyncClient(app=app, base_url=URL) as ac:
        response = await ac.get("/nonexistent-page")

    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

    assert response.status_code == 404, "Expected 404 for nonexistent page"


@pytest.mark.asyncio
async def test_upload_valid_image():
    async with AsyncClient(app=app, base_url=URL) as ac:
        with open(GOOD_IMAGE_PATH, "rb") as image_file:
            files = {"avatar": ("ava.jpg", image_file, "image/jpeg")}
            data = {
                "email": "image_test_user2@example.com",
                "password": "securepassword",
                "first_name": "Image",
                "last_name": "Tester",
                "gender": "female"
            }
            response = await ac.post("/api/clients/create", files=files, data=data)

    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

    assert response.status_code == 201
    assert response.json()["email"] == "image_test_user2@example.com"

    user_id = response.json()["id"]

    # Удаляем созданного ранее пользователя
    async with AsyncSession(engine) as session:
        user_service = UserService(session, PasswordHasherProtocol)
        await user_service.delete_user_by_id(user_id)


@pytest.mark.asyncio
async def test_double_register():
    async with AsyncClient(app=app, base_url=URL) as ac:
        with open(GOOD_IMAGE_PATH, "rb") as image_file:
            files = {"avatar": ("ava.jpg", image_file, "image/jpeg")}
            data = {
                "email": "image_test_user2@example.com",
                "password": "securepassword",
                "first_name": "Image",
                "last_name": "Tester",
                "gender": "female"
            }
            response = await ac.post("/api/clients/create", files=files, data=data)
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            user_id = response.json()["id"]
            response = await ac.post("/api/clients/create", files=files, data=data)

    print(f"Second Response status: {response.status_code}")
    print(f"Second Response body: {response.text}")

    # Удаляем созданного ранее пользователя
    async with AsyncSession(engine) as session:
        user_service = UserService(session, PasswordHasherProtocol)
        await user_service.delete_user_by_id(user_id)

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_invalid_email():
    async with AsyncClient(app=app, base_url=URL) as ac:
        with open(GOOD_IMAGE_PATH, "rb") as image_file:
            files = {"avatar": ("ava.jpg", image_file, "image/jpeg")}
            data = {
                "email": "example.com",
                "password": "securepassword",
                "first_name": "Image",
                "last_name": "Tester",
                "gender": "female"
            }
            response = await ac.post("/api/clients/create", files=files, data=data)

    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_password():
    async with AsyncClient(app=app, base_url=URL) as ac:
        with open(GOOD_IMAGE_PATH, "rb") as image_file:
            files = {"avatar": ("ava.jpg", image_file, "image/jpeg")}
            data = {
                "email": "uuu@example.com",
                "password": "se",
                "first_name": "Image",
                "last_name": "Tester",
                "gender": "female"
            }
            response = await ac.post("/api/clients/create", files=files, data=data)

    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_user_by_id():
    async with AsyncClient(app=app, base_url=URL) as ac:
        response = await ac.get(f"/api/clients/1")  # Считаем что 1 существует
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

    assert response.status_code == 200
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_get_nonexistent_user_by_id():
    async with AsyncClient(app=app, base_url=URL) as ac:
        response = await ac.get("/api/clients/99999")  # Считаем что 99999 не существует

    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

    assert response.status_code == 404, "Expected 404 for nonexistent user ID"


@pytest.mark.asyncio
async def test_upload_invalid_image():
    async with AsyncClient(app=app, base_url=URL) as ac:
        with open(BAD_IMAGE_PATH, "rb") as text_file:
            files = {"avatar": ("ava.txt", text_file, "text/plain")}
            data = {
                "email": "invalid_image_test_user@example.com",
                "password": "securepassword",
                "first_name": "Invalid",
                "last_name": "Tester",
                "gender": "male"
            }
            response = await ac.post("/api/clients/create", files=files, data=data)

    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

    assert response.status_code == 400
    assert "не является корректным" in response.json()["detail"]
