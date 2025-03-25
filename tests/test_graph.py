# test_graph.py
import pytest
from AgenticWorkflow.graph import graph
from AgenticWorkflow.utils.state import State
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_graph_happy_path():
    test_input = {"question": "Names of students in Lincoln school?"}
    
    with patch('AgenticWorkflow.utils.nodes.query_permission_node', new_callable=AsyncMock) as mock_permission, \
         patch('AgenticWorkflow.utils.nodes.query_relevant_node', new_callable=AsyncMock) as mock_relevant, \
         patch('AgenticWorkflow.utils.nodes.query_decision_node', new_callable=AsyncMock) as mock_decision, \
         patch('AgenticWorkflow.utils.nodes.sql_query_formulation_node', new_callable=AsyncMock) as mock_formulation, \
         patch('AgenticWorkflow.utils.nodes.sql_query_node', new_callable=AsyncMock) as mock_query, \
         patch('AgenticWorkflow.utils.nodes.query_answer_node', new_callable=AsyncMock) as mock_answer:
        
        # Setup mocks
        mock_permission.return_value = {"permitted": True}
        mock_relevant.return_value = {"relevant": True}
        mock_decision.return_value = {"decision": "input permitted"}
        mock_formulation.return_value = {"sql_query": "SELECT * FROM students LIMIT 5"}
        mock_query.return_value = {"raw_answer": "[('John',), ('Jane',)]", "sql_error": ""}
        mock_answer.return_value = {"answer": "The students are John and Jane"}
        
        # Execute
        result = await graph.ainvoke(test_input, config={"thread_id": "123"})
        
        # Assertions
        assert "answer" in result
        assert "John" in result["answer"]
        assert "Jane" in result["answer"]

@pytest.mark.asyncio
async def test_graph_not_relevant():
    test_input = {"question": "What's the weather today?"}
    
    with patch('AgenticWorkflow.utils.nodes.query_permission_node', new_callable=AsyncMock) as mock_permission, \
         patch('AgenticWorkflow.utils.nodes.query_relevant_node', new_callable=AsyncMock) as mock_relevant, \
         patch('AgenticWorkflow.utils.nodes.query_decision_node', new_callable=AsyncMock) as mock_decision, \
         patch('AgenticWorkflow.utils.nodes.update_output', new_callable=AsyncMock) as mock_update:
        
        # Setup mocks
        mock_permission.return_value = {"permitted": True}
        mock_relevant.return_value = {"relevant": False}
        mock_decision.return_value = {"decision": "input not permitted"}
        mock_update.return_value = {"output": "Your question is not relevant or not permitted."}
        
        # Execute
        result = await graph.ainvoke(test_input, config={"thread_id": "123"})
        
        # Assertions
        assert "output" in result
        assert "not relevant" in result["output"]