# test_schemas.py
import pytest
from AgenticWorkflow.utils.schemas import (
    PermissionSchema,
    CheckRelevance,
    QueryFormulationSchema,
    QueryAnswerSchema
)

def test_permission_schema():
    data = {"permitted": True}
    schema = PermissionSchema(**data)
    assert schema.permitted is True

def test_check_relevance_schema():
    data = {"relevance": "relevant"}
    schema = CheckRelevance(**data)
    assert schema.relevance == "relevant"

def test_query_formulation_schema():
    data = {"sql_query": "SELECT * FROM students"}
    schema = QueryFormulationSchema(**data)
    assert schema.sql_query == "SELECT * FROM students"

def test_query_answer_schema():
    data = {"answer": "The answer is 42"}
    schema = QueryAnswerSchema(**data)
    assert schema.answer == "The answer is 42"