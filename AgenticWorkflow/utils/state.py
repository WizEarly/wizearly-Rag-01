from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing import Annotated

class InputState(TypedDict):
    question: str
    
class OutputState(TypedDict):
    answer: str
    
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    question: str
    permitted: bool
    relevant: bool
    decision: str
    sql_query: str
    sql_error: str
    raw_answer: str
    answer: str

