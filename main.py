from fastapi import FastAPI
from pydantic import BaseModel
from AgenticWorkflow.graph import graph

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    
    
@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    answer = graph.invoke(input={"question": request.question}, config={"thread_id": "123"})
    return QueryResponse(answer=answer["answer"])

@app.get("/")
def read_root():
    return {"Welcome Speech": "Ahem!! Welcome to the School Rag System🥸"}