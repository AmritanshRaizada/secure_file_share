import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.models.user import User
import motor.motor_asyncio

client = TestClient(app)

@pytest.fixture
async def db():
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    yield db
    await db.drop_collection("users")
    client.close()

@pytest.mark.asyncio
async def test_signup_success(db):
    test_user = {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "securepassword123"
    }
    
    response = client.post("/auth/signup", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["full_name"] == test_user["full_name"]
    assert data["is_verified"] is False
    assert "hashed_password" not in data

@pytest.mark.asyncio
async def test_signup_duplicate_email(db):
    test_user = {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "securepassword123"
    }
    
    # First signup should succeed
    response = client.post("/auth/signup", json=test_user)
    assert response.status_code == 200
    
    # Second signup with same email should fail
    response = client.post("/auth/signup", json=test_user)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_login_success(db):
    # First signup
    test_user = {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "securepassword123"
    }
    signup_response = client.post("/auth/signup", json=test_user)
    assert signup_response.status_code == 200
    
    # Verify email (in a real test, we'd extract the token from the mock email)
    user = await db["users"].find_one({"email": test_user["email"]})
    verification_token = user["verification_token"]
    verify_response = client.get(f"/auth/verify-email?token={verification_token}")
    assert verify_response.status_code == 200
    
    # Then login
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }
    login_response = client.post("/auth/login", data=login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

@pytest.mark.asyncio
async def test_login_unverified(db):
    # Signup but don't verify
    test_user = {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "securepassword123"
    }
    signup_response = client.post("/auth/signup", json=test_user)
    assert signup_response.status_code == 200
    
    # Attempt login
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }
    login_response = client.post("/auth/login", data=login_data)
    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Email not verified"