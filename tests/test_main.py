# test_main.py
import pytest
from fastapi.testclient import TestClient
from main import app, QueryRequest
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome Speech" in response.json()
    assert "School Rag System" in response.json()["Welcome Speech"]

@patch('main.graph')
def test_handle_query_success(mock_graph):
    # Setup mock
    mock_response = {"answer": "Test answer"}
    mock_graph.invoke.return_value = mock_response
    
    # Test request
    test_request = {"question": "Test question"}
    response = client.post("/query", json=test_request)
    
    # Assertions
    assert response.status_code == 200
    assert response.json() == {"answer": "Test answer"}
    mock_graph.invoke.assert_called_once_with(
        input={"question": "Test question"},
        config={"thread_id": "123"}
    )

@patch('main.graph')
def test_handle_query_empty_question(mock_graph):
    response = client.post("/query", json={"question": ""})
    assert response.status_code == 422  # Validation error

def test_query_request_model():
    # Test valid request
    valid_request = QueryRequest(question="Valid question")
    assert valid_request.question == "Valid question"
    
    # Test invalid request
    with pytest.raises(ValueError):
        QueryRequest(question=None)