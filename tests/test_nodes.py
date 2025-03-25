# test_nodes.py
import pytest
from AgenticWorkflow.utils.nodes import *
from AgenticWorkflow.utils.state import State
from unittest.mock import patch

def test_query_permission_node():
    state = {"question": "Test question"}
    result = query_permission_node(state)
    assert result == {"permitted": True}

@pytest.mark.asyncio
async def test_query_relevant_node_relevant():
    test_state = {"question": "Student names"}
    with patch('AgenticWorkflow.utils.nodes.create_react_agent') as mock_agent:
        mock_agent.return_value.invoke.return_value = {
            "messages": [{"content": "relevant"}]
        }
        result = await query_relevant_node(test_state)
        assert result == {"relevant": True}

@pytest.mark.asyncio
async def test_query_relevant_node_not_relevant():
    test_state = {"question": "Weather forecast"}
    with patch('AgenticWorkflow.utils.nodes.create_react_agent') as mock_agent:
        mock_agent.return_value.invoke.return_value = {
            "messages": [{"content": "not_relevant"}]
        }
        result = await query_relevant_node(test_state)
        assert result == {"relevant": False}

def test_query_decision_node_permitted():
    state = {"permitted": True, "relevant": True}
    result = query_decision_node(state)
    assert result == {"decision": "input permitted"}

def test_query_decision_node_not_permitted():
    state = {"permitted": False, "relevant": True}
    result = query_decision_node(state)
    assert result == {"decision": "input not permitted"}

@pytest.mark.asyncio
async def test_sql_query_formulation_node():
    test_state = {"question": "Student names"}
    with patch('AgenticWorkflow.utils.nodes.create_react_agent') as mock_agent:
        mock_agent.return_value.invoke.return_value = {
            "messages": [{"content": "SELECT * FROM students"}]
        }
        result = await sql_query_formulation_node(test_state)
        assert "sql_query" in result

@pytest.mark.asyncio
async def test_sql_query_node_success():
    test_state = {"sql_query": "SELECT * FROM students"}
    with patch('AgenticWorkflow.utils.db.db.run') as mock_run:
        mock_run.return_value = "[('John',), ('Jane',)]"
        result = await sql_query_node(test_state)
        assert "raw_answer" in result
        assert "sql_error" in result
        assert result["sql_error"] == ""

@pytest.mark.asyncio
async def test_sql_query_node_error():
    test_state = {"sql_query": "INVALID SQL"}
    with patch('AgenticWorkflow.utils.db.db.run', side_effect=Exception("SQL error")):
        result = await sql_query_node(test_state)
        assert "sql_error" in result
        assert "SQL error" in result["sql_error"]

def test_route_sql_error_with_error():
    state = {"sql_error": "Error message"}
    result = route_sql_error(state)
    assert result == "sql_query_formulation_node"

def test_route_sql_error_no_error():
    state = {"sql_error": ""}
    result = route_sql_error(state)
    assert result == "query_answer_node"

@pytest.mark.asyncio
async def test_query_answer_node():
    test_state = {
        "question": "Who are the students?",
        "raw_answer": "[('John',), ('Jane',)]"
    }
    with patch('AgenticWorkflow.utils.nodes.StrOutputParser') as mock_parser:
        mock_parser.return_value.invoke.return_value = "The students are John and Jane"
        result = await query_answer_node(test_state)
        assert "answer" in result
        assert "John" in result["answer"]
        assert "Jane" in result["answer"]