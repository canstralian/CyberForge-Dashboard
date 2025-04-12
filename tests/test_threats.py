"""
Tests for threat-related endpoints.
"""
import pytest
from fastapi import status
import json

@pytest.mark.asyncio
async def test_get_threats(authorized_client, test_threats):
    """Test get threats."""
    response = authorized_client.get("/api/v1/threats")
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 5
    assert response.json()[0]["title"] == "Test Threat 0"

@pytest.mark.asyncio
async def test_get_threat_by_id(authorized_client, test_threats):
    """Test get threat by ID."""
    response = authorized_client.get(f"/api/v1/threats/{test_threats[0].id}")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Test Threat 0"
    assert response.json()["id"] == test_threats[0].id

@pytest.mark.asyncio
async def test_get_threat_by_id_not_found(authorized_client):
    """Test get threat by ID not found."""
    response = authorized_client.get("/api/v1/threats/9999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_create_threat(authorized_client):
    """Test create threat."""
    response = authorized_client.post(
        "/api/v1/threats",
        json={
            "title": "New Threat",
            "description": "New description",
            "severity": "Medium",
            "status": "New",
            "category": "Data Breach",
            "source_url": "https://example.com/new-threat",
            "source_name": "Test Source",
            "confidence_score": 0.8,
            "risk_score": 0.6
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["title"] == "New Threat"
    assert response.json()["severity"] == "Medium"
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_update_threat(authorized_client, test_threats):
    """Test update threat."""
    response = authorized_client.put(
        f"/api/v1/threats/{test_threats[0].id}",
        json={
            "title": "Updated Threat",
            "severity": "High"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Updated Threat"
    assert response.json()["severity"] == "High"
    assert response.json()["id"] == test_threats[0].id

@pytest.mark.asyncio
async def test_update_threat_not_found(authorized_client):
    """Test update threat not found."""
    response = authorized_client.put(
        "/api/v1/threats/9999",
        json={
            "title": "Updated Threat"
        }
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_delete_threat(authorized_client, test_threats):
    """Test delete threat."""
    response = authorized_client.delete(f"/api/v1/threats/{test_threats[0].id}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify threat is deleted
    get_response = authorized_client.get(f"/api/v1/threats/{test_threats[0].id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_threat_not_found(authorized_client):
    """Test delete threat not found."""
    response = authorized_client.delete("/api/v1/threats/9999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_get_threat_statistics(authorized_client, test_threats):
    """Test get threat statistics."""
    response = authorized_client.get("/api/v1/threats/statistics")
    
    assert response.status_code == status.HTTP_200_OK
    assert "total_count" in response.json()
    assert "by_severity" in response.json()
    assert "by_status" in response.json()
    assert "by_category" in response.json()
    assert "latest_threats" in response.json()