from langchain_together import ChatTogether
from dotenv import load_dotenv, find_dotenv
from AgenticWorkflow.utils.schemas import PermissionSchema, CheckRelevance, QueryFormulationSchema, QueryAnswerSchema

load_dotenv(find_dotenv())

llm = ChatTogether(
    model="meta-llama/Llama-3.3-70b-Instruct-Turbo",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

permission_llm = llm.with_structured_output(PermissionSchema)
verification_llm = llm.with_structured_output(CheckRelevance)
qf_llm = llm.with_structured_output(QueryFormulationSchema)
qa_llm = llm.with_structured_output(QueryAnswerSchema)
