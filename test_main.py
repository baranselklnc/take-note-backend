"""Test cases for the Take Note Backend API."""

import pytest
import httpx
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import json

from main import app
from models import NoteCreate, NoteUpdate, NoteResponse
from exceptions import NoteNotFoundError, NoteAccessDeniedError

# Create test client
client = TestClient(app)


class TestNotesAPI:
    """Test cases for notes endpoints."""
    
    def setup_method(self):
        """Setup test data."""
        self.test_user_id = "test-user-123"
        self.test_note_id = "test-note-456"
        self.test_note_data = {
            "title": "Test Note",
            "content": "This is a test note content",
            "is_pinned": False
        }
        self.test_note_response = {
            "id": self.test_note_id,
            "user_id": self.test_user_id,
            "title": "Test Note",
            "content": "This is a test note content",
            "is_pinned": False,
            "is_deleted": False,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": None,
            "deleted_at": None
        }
    
    @patch('auth.auth_manager.get_current_user')
    def test_get_notes_success(self, mock_auth):
        """Test successful retrieval of notes."""
        mock_auth.return_value = {"user_id": self.test_user_id}
        
        with patch('database.db_manager.get_user_notes') as mock_db:
            mock_db.return_value = [self.test_note_response]
            
            response = client.get("/notes")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert len(data["notes"]) == 1
            assert data["notes"][0]["id"] == self.test_note_id
    
    @patch('auth.auth_manager.get_current_user')
    def test_create_note_success(self, mock_auth):
        """Test successful note creation."""
        mock_auth.return_value = {"user_id": self.test_user_id}
        
        with patch('database.db_manager.create_note') as mock_db:
            mock_db.return_value = self.test_note_response
            
            response = client.post("/notes", json=self.test_note_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["id"] == self.test_note_id
            assert data["title"] == self.test_note_data["title"]
            assert data["content"] == self.test_note_data["content"]
    
    @patch('auth.auth_manager.get_current_user')
    def test_get_note_success(self, mock_auth):
        """Test successful retrieval of a specific note."""
        mock_auth.return_value = {"user_id": self.test_user_id}
        
        with patch('database.db_manager.get_note_by_id') as mock_db:
            mock_db.return_value = self.test_note_response
            
            response = client.get(f"/notes/{self.test_note_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == self.test_note_id
    
    @patch('auth.auth_manager.get_current_user')
    def test_get_note_not_found(self, mock_auth):
        """Test note not found scenario."""
        mock_auth.return_value = {"user_id": self.test_user_id}
        
        with patch('database.db_manager.get_note_by_id') as mock_db:
            mock_db.return_value = None
            
            response = client.get(f"/notes/{self.test_note_id}")
            
            assert response.status_code == 404
            data = response.json()
            assert "not found" in data["error"].lower()
    
    @patch('auth.auth_manager.get_current_user')
    def test_update_note_success(self, mock_auth):
        """Test successful note update."""
        mock_auth.return_value = {"user_id": self.test_user_id}
        
        updated_note = self.test_note_response.copy()
        updated_note["title"] = "Updated Title"
        updated_note["content"] = "Updated content"
        
        with patch('database.db_manager.get_note_by_id') as mock_get, \
             patch('database.db_manager.update_note') as mock_update:
            
            mock_get.return_value = self.test_note_response
            mock_update.return_value = updated_note
            
            update_data = {
                "title": "Updated Title",
                "content": "Updated content"
            }
            
            response = client.put(f"/notes/{self.test_note_id}", json=update_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Updated Title"
            assert data["content"] == "Updated content"
    
    @patch('auth.auth_manager.get_current_user')
    def test_delete_note_success(self, mock_auth):
        """Test successful note deletion."""
        mock_auth.return_value = {"user_id": self.test_user_id}
        
        with patch('database.db_manager.get_note_by_id') as mock_get, \
             patch('database.db_manager.soft_delete_note') as mock_delete:
            
            mock_get.return_value = self.test_note_response
            mock_delete.return_value = True
            
            response = client.delete(f"/notes/{self.test_note_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert "deleted successfully" in data["message"]
    
    @patch('auth.auth_manager.get_current_user')
    def test_toggle_pin_success(self, mock_auth):
        """Test successful pin toggle."""
        mock_auth.return_value = {"user_id": self.test_user_id}
        
        pinned_note = self.test_note_response.copy()
        pinned_note["is_pinned"] = True
        
        with patch('database.db_manager.toggle_pin_note') as mock_db:
            mock_db.return_value = pinned_note
            
            response = client.patch(f"/notes/{self.test_note_id}/pin")
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_pinned"] is True
    
    @patch('auth.auth_manager.get_current_user')
    def test_search_notes_success(self, mock_auth):
        """Test successful note search."""
        mock_auth.return_value = {"user_id": self.test_user_id}
        
        with patch('database.db_manager.search_notes') as mock_db:
            mock_db.return_value = [self.test_note_response]
            
            response = client.post("/notes/search", json={"query": "test"})
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["notes"]) == 1
            assert data["notes"][0]["id"] == self.test_note_id
    
    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints."""
        response = client.get("/notes")
        assert response.status_code == 401
    
    def test_create_note_validation_error(self):
        """Test note creation with invalid data."""
        with patch('auth.auth_manager.get_current_user') as mock_auth:
            mock_auth.return_value = {"user_id": self.test_user_id}
            
            invalid_data = {
                "title": "",  # Empty title should fail validation
                "content": "Valid content"
            }
            
            response = client.post("/notes", json=invalid_data)
            assert response.status_code == 422
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Take Note Backend API is running" in data["message"]
    
    def test_health_check(self):
        """Test health check endpoint."""
        with patch('database.db_manager.get_user_notes') as mock_db:
            mock_db.return_value = []
            
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"


class TestPagination:
    """Test pagination functionality."""
    
    @patch('auth.auth_manager.get_current_user')
    def test_pagination_params(self, mock_auth):
        """Test pagination parameters."""
        mock_auth.return_value = {"user_id": "test-user"}
        
        with patch('database.db_manager.get_user_notes') as mock_db:
            mock_db.return_value = []
            
            response = client.get("/notes?page=2&size=10")
            assert response.status_code == 200
            
            data = response.json()
            assert data["page"] == 2
            assert data["size"] == 10
    
    @patch('auth.auth_manager.get_current_user')
    def test_invalid_pagination_params(self, mock_auth):
        """Test invalid pagination parameters."""
        mock_auth.return_value = {"user_id": "test-user"}
        
        with patch('database.db_manager.get_user_notes') as mock_db:
            mock_db.return_value = []
            
            # Test negative page number
            response = client.get("/notes?page=-1")
            assert response.status_code == 422
            
            # Test size too large
            response = client.get("/notes?size=1000")
            assert response.status_code == 422


class TestSearch:
    """Test search functionality."""
    
    @patch('auth.auth_manager.get_current_user')
    def test_search_with_query_param(self, mock_auth):
        """Test search using query parameter."""
        mock_auth.return_value = {"user_id": "test-user"}
        
        with patch('database.db_manager.search_notes') as mock_db:
            mock_db.return_value = []
            
            response = client.get("/notes?search=test")
            assert response.status_code == 200
    
    @patch('auth.auth_manager.get_current_user')
    def test_search_endpoint(self, mock_auth):
        """Test dedicated search endpoint."""
        mock_auth.return_value = {"user_id": "test-user"}
        
        with patch('database.db_manager.search_notes') as mock_db:
            mock_db.return_value = []
            
            search_data = {"query": "test", "limit": 10}
            response = client.post("/notes/search", json=search_data)
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
