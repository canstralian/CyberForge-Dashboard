"""
Tests for authentication endpoints.
"""
import pytest
from fastapi import status
from httpx import AsyncClient
import json

from src.api.main import app

@pytest.mark.asyncio
async def test_login_success(client, test_user):
    """Test login success."""
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_login_user_not_found(client, test_user):
    """Test login with nonexistent user."""
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "nonexistentuser",
            "password": "testpassword"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_register_success(client, setup_database):
    """Test register success."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
            "full_name": "New User",
            "is_active": True
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["username"] == "newuser"
    assert response.json()["email"] == "newuser@example.com"
    assert "hashed_password" not in response.json()

@pytest.mark.asyncio
async def test_register_duplicate_username(client, test_user):
    """Test register with duplicate username."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "newpassword",
            "full_name": "Test User",
            "is_active": True
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_protected_endpoint_with_token(authorized_client):
    """Test protected endpoint with token."""
    response = authorized_client.get("/api/v1/threats")
    
    assert response.status_code != status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client):
    """Test protected endpoint without token."""
    response = client.get("/api/v1/threats")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()