from AgenticWorkflow.utils.state import State, InputState, OutputState
from langchain_core.prompts import PromptTemplate
from AgenticWorkflow.utils.models import llm
from langgraph.prebuilt import create_react_agent
from AgenticWorkflow.utils.db import db
from AgenticWorkflow.utils.tools import relevance_tools
from langchain_core.messages import SystemMessage
from AgenticWorkflow.utils.schemas import QueryFormulationSchema
from langchain_core.output_parsers.string import StrOutputParser

def query_permission_node(state: InputState) -> State:
    return {"permitted": True}

def query_relevant_node(state: State):
    system = """You are an assistant that determines whether a given question is related to the following {dialect} database schema.
    Get the table names that are related to the question from the tool ListSQLDatabaseTool
    Then get the schema for the table names from the tool InfoSQLDatabaseTool
    
    Respond with only "relevant" or "not_relevant".
    """
    prompt_template = PromptTemplate.from_template(system)
    relevance_system_message = prompt_template.format(dialect=db.dialect)
    agent = create_react_agent(llm, relevance_tools, prompt=SystemMessage(relevance_system_message))
    is_relevant_invoke = agent.invoke(
        {"messages": [{"role": "user", "content": state['question']}]},
    )
    if is_relevant_invoke['messages'][-1].content == "relevant":
        return {"relevant": True} 
    return {"relevant": False}

def query_decision_node(state: State):
    """A decision node to decide if a user input is permitted or not."""
    decision = state['permitted'] and state['relevant']
    if decision:
        return {"decision": "input permitted"}
    return {"decision": "input not permitted"}

def sql_query_formulation_node(state: State):
    if state.get("sql_error"):
        system = """You are an assistant that converts natural language questions into SQL queries based on the following schema:
        Get the table names that are related to the question from the tool ListSQLDatabaseTool
        Then get the schema for the table names from the tool InfoSQLDatabaseTool
        
        Provide only the {dialect} SQL query without any explanations. Alias columns appropriately to match the expected keys in the result.
        
        For example, alias 'food.name' as 'food_name' and 'food.price' as 'price'.

        If it asks for a list only return the first 5

        You had a previous SQL error: {sql_error}, for this query: {sql_query}, ensure the new query corrects the issue.
        """
        
        prompt_template = PromptTemplate.from_template(system)
        qf_system_message = prompt_template.format(dialect=db, sql_error = state.get("sql_error"), sql_query=state.get("sql_query"))
        agent = create_react_agent(llm, relevance_tools, prompt=SystemMessage(qf_system_message), response_format=QueryFormulationSchema)
        qf_invoke = agent.invoke(
            {"messages": [{"role": "user", "content": state['question']}]},
        )
    else:
        system = """You are an assistant that converts natural language questions into SQL queries based on the following schema:
        Get the table names that are related to the question from the tool ListSQLDatabaseTool
        Then get the schema for the table names from the tool InfoSQLDatabaseTool
        
        Provide only the {dialect} SQL query without any explanations. Alias columns appropriately to match the expected keys in the result.
        
        For example, alias 'food.name' as 'food_name' and 'food.price' as 'price'.

        If it asks for a list only return the first 5
        """
        
        prompt_template = PromptTemplate.from_template(system)
        qf_system_message = prompt_template.format(dialect=db)
        agent = create_react_agent(llm, relevance_tools, prompt=SystemMessage(qf_system_message), response_format=QueryFormulationSchema)
        qf_invoke = agent.invoke(
            {"messages": [{"role": "user", "content": state['question']}]},
        )
        
    return {"sql_query": qf_invoke["messages"][-1].content}

def sql_query_node(state: State):
    try:
        answer = db.run(state['sql_query'])
        return {"raw_answer": answer, "sql_error": ""}  # Clear previous errors if successful
    except Exception as e:
        return {"sql_error": str(e)}
    
def route_sql_error(state: State):
    if state.get("sql_error"):
        return "sql_query_formulation_node"  # Retry query formulation if there's an error
    return "query_answer_node"

def query_answer_node(state: State) -> OutputState:
    prompt = """
    You are an assistant that converts answers from an sql query to a natural language answer while also using the user question:
    The question is {question}
    The sql answer is {answer}

    Reply with only a natural language answer for the user in a friendly manner.
    """
    prompt_template = PromptTemplate.from_template(prompt)
    chain = prompt_template | llm | StrOutputParser()
    answer = chain.invoke({
        "question": state['question'],
        "answer": state["raw_answer"]
    })

    return {"answer": answer}

def route_decision(state: State):
    print(state['decision'])
    if state['decision'] == "input permitted":
        return "sql_query_formulation_node"
    else:
        return "end"
    
def update_output(state: State):
    return {"output": "Your question is not relevant or not permitted."}