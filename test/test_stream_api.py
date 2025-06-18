import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from stream_api import app, get_db_connection


client = TestClient(app)

# Sample fake data to return from the mock DB
fake_data = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
]


@patch("stream_api.get_db_connection")
def test_get_data_success(mock_get_conn):
    # Create mock cursor behavior
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    # Configure return values
    mock_cursor.fetchall.return_value = fake_data
    mock_conn.cursor.return_value = mock_cursor
    mock_get_conn.return_value = mock_conn

    # Make request to FastAPI endpoint
    response = client.get("/data?offset=0&limit=2")

    # Assertions
    assert response.status_code == 200
    assert response.json() == fake_data

    # Verify SQL execution
    mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table LIMIT %s OFFSET %s", (2, 0))
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
