from typing_extensions import Literal
from pydantic import BaseModel, Field
from typing import Optional
class PermissionSchema(BaseModel):
    """
    Schema for determining whether a user input is permitted.
    
    Attributes:
        permitted (bool): Indicates whether the input is allowed. 
                          - True: The input is permitted.
                          - False: The input is not permitted.
    """
    permitted: Literal[True, False] = Field(False, descripiton = "Indicates whether the user input is allowed.")

class CheckRelevance(BaseModel):
    relevance: str = Field(
        description="Indicates whether the question is related to the database schema. 'relevant' or 'not_relevant'."
    )

class QueryFormulationSchema(BaseModel):
    """
    Schema for generating an SQL query that retrieves the answer to a user input.
    
    Attributes:
        sql_query (str): The SQL query formulated based on the user's request. 
                         - This query should be executable on the target database.
                         - It should be structured to return the relevant data answering the user's input.
                         - If the query cannot be formulated, this field may be None.
    """
    sql_query: Optional[str] = Field(None, description = "The generated SQL query that corresponds to the user's input.")

class QueryAnswerSchema(BaseModel):
    """
    Schema for generating an answer based on the user's input and the retrieved database results.

    Attributes:
        answer (str): The final response generated using the user's input and the query results.
                      - This answer should be meaningful and relevant to the user's request.
                      - If no relevant data is found, this field may contain an appropriate message.
    """
    answer: str = Field(description="The response generated from the database query and the user's input.")