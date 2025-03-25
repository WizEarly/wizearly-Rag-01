from langgraph.graph import StateGraph, START, END
from AgenticWorkflow.utils.state import State, InputState, OutputState
from langgraph.checkpoint.memory import MemorySaver
from AgenticWorkflow.utils.nodes import (
    query_answer_node, 
    query_decision_node, 
    query_permission_node, 
    query_relevant_node, 
    sql_query_formulation_node, 
    sql_query_node,
    route_decision,
    route_sql_error,
    update_output,
)

workflow = StateGraph(State, input=InputState, output=OutputState)

workflow.add_node("query_permission_node", query_permission_node)
workflow.add_node("query_relevant_node", query_relevant_node)
workflow.add_node("query_decision_node", query_decision_node)
workflow.add_node("sql_query_formulation_node", sql_query_formulation_node)
workflow.add_node("sql_query_node", sql_query_node)
workflow.add_node("query_answer_node", query_answer_node)
workflow.add_node("update_output", update_output)

workflow.add_edge(START, "query_permission_node")
workflow.add_edge(START, "query_relevant_node")
workflow.add_edge("query_permission_node", "query_decision_node")
workflow.add_edge("query_relevant_node", "query_decision_node")
workflow.add_conditional_edges(
    "query_decision_node", 
    route_decision, 
    {
        "sql_query_formulation_node": "sql_query_formulation_node",
        "end": "update_output"
    }
)
workflow.add_edge("sql_query_formulation_node", "sql_query_node")
workflow.add_conditional_edges(
    "sql_query_node", 
    route_sql_error, 
    {
        "sql_query_formulation_node": "sql_query_formulation_node",  # Retry on error
        "query_answer_node": "query_answer_node"  # Proceed if successful
    }
)
workflow.add_edge("update_output", END)
workflow.add_edge("query_answer_node", END)

checkpoint = MemorySaver()

graph = workflow.compile(checkpointer=checkpoint)

