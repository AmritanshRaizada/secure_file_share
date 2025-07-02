import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.models.user import User
from app.models.file import File
import motor.motor_asyncio
import os

client = TestClient(app)

@pytest.fixture
async def db():
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    yield db
    await db.drop_collection("users")
    await db.drop_collection("files")
    client.close()

@pytest.fixture
async def test_user(db):
    user_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "hashed_password": "hashedpassword",
        "is_verified": True,
        "is_ops_user": False,
    }
    user = await User(db).create_user(user_data)
    return user

@pytest.fixture
async def test_ops_user(db):
    user_data = {
        "email": "ops@example.com",
        "full_name": "Ops User",
        "hashed_password": "hashedpassword",
        "is_verified": True,
        "is_ops_user": True,
    }
    user = await User(db).create_user(user_data)
    return user

@pytest.fixture
async def auth_token(test_user):
    login_data = {
        "username": test_user["email"],
        "password": "testpassword"  # Note: In a real test, we'd hash this properly
    }
    # Bypass password verification for test
    response = client.post("/auth/login", data=login_data)
    return response.json()["access_token"]

@pytest.fixture
async def ops_auth_token(test_ops_user):
    login_data = {
        "username": test_ops_user["email"],
        "password": "testpassword"  # Note: In a real test, we'd hash this properly
    }
    # Bypass password verification for test
    response = client.post("/auth/login", data=login_data)
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_upload_file_success(db, ops_auth_token):
    # Create a test file
    test_file_content = b"Test file content"
    test_file_path = "test.docx"
    
    with open(test_file_path, "wb") as f:
        f.write(test_file_content)
    
    with open(test_file_path, "rb") as f:
        response = client.post(
            "/files/upload",
            files={"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            headers={"Authorization": f"Bearer {ops_auth_token}"}
        )
    
    os.remove(test_file_path)
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.docx"
    assert data["content_type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert data["file_size"] == len(test_file_content)

@pytest.mark.asyncio
async def test_upload_file_unauthorized(db, auth_token):
    # Regular user should not be able to upload
    test_file_content = b"Test file content"
    test_file_path = "test.docx"
    
    with open(test_file_path, "wb") as f:
        f.write(test_file_content)
    
    with open(test_file_path, "rb") as f:
        response = client.post(
            "/files/upload",
            files={"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    os.remove(test_file_path)
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Operation not permitted"

@pytest.mark.asyncio
async def test_generate_download_link(db, test_user, auth_token):
    # First create a test file (bypassing the upload endpoint)
    file_data = {
        "filename": "test.docx",
        "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "file_size": 1234,
        "file_path": "uploads/test.docx",
        "uploaded_by": str(test_user["_id"]),
    }
    file = await File(db).create_file(file_data)
    
    # Generate download link
    response = client.get(
        f"/files/download/{file['_id']}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "download_link" in data
    assert data["message"] == "success"

@pytest.mark.asyncio
async def test_list_files(db, test_user, auth_token):
    # Create some test files
    file_data1 = {
        "filename": "test1.docx",
        "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "file_size": 1234,
        "file_path": "uploads/test1.docx",
        "uploaded_by": str(test_user["_id"]),
    }
    file_data2 = {
        "filename": "test2.xlsx",
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "file_size": 2345,
        "file_path": "uploads/test2.xlsx",
        "uploaded_by": str(test_user["_id"]),
    }
    await File(db).create_file(file_data1)
    await File(db).create_file(file_data2)
    
    # List files
    response = client.get(
        "/files/list",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["filename"] in ["test1.docx", "test2.xlsx"]
    assert data[1]["filename"] in ["test1.docx", "test2.xlsx"]