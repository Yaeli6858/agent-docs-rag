import os
import ssl
import urllib3
import httpx
import asyncio
from dotenv import load_dotenv

# --- 1. הגדרות SSL אגרסיביות לנטפרי ---
if "SSL_CERT_FILE" in os.environ:
    del os.environ["SSL_CERT_FILE"]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

def patched_init(self, *args, **kwargs):
    kwargs['verify'] = False
    return original_init(self, *args, **kwargs)

original_init = httpx.Client.__init__
httpx.Client.__init__ = patched_init

original_async_init = httpx.AsyncClient.__init__
def patched_async_init(self, *args, **kwargs):
    kwargs['verify'] = False
    return original_async_init(self, *args, **kwargs)
httpx.AsyncClient.__init__ = patched_async_init
# ------------------------------------

from llama_index.core.workflow import (
    Event, 
    Workflow, 
    step, 
    Context, 
    StartEvent, 
    StopEvent
)
from llama_index.core.base.llms.types import ChatMessage
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.cohere import Cohere
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex

load_dotenv()

class RetrievalEvent(Event):
    nodes: list
    query: str

class ValidationEvent(Event):
    nodes: list
    query: str

class RAGWorkflow(Workflow):
    _llm = None

    def get_llm(self):
        if self._llm is None:
            self._llm = Cohere(
                api_key=os.environ.get("COHERE_API_KEY"), 
                model="command-r-08-2024"
            )
        return self._llm

    @step
    async def setup(self, ctx: Context, ev: StartEvent) -> RetrievalEvent:
        print(f"--- Step: Retrieval ({ev.query}) ---")
        embed_model = CohereEmbedding(api_key=os.environ.get("COHERE_API_KEY"), model_name="embed-multilingual-v3.0")
        
        pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"), ssl_verify=False)
        pinecone_index = pc.Index("code-docs-index")
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        
        index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
        retriever = index.as_retriever(similarity_top_k=3)
        nodes = retriever.retrieve(ev.query)
        
        return RetrievalEvent(nodes=nodes, query=ev.query)

    @step
    async def validate(self, ctx: Context, ev: RetrievalEvent) -> ValidationEvent | StopEvent:
        print("--- Step: Validation ---")
        if not ev.nodes:
            return StopEvent(result="מצטער, לא מצאתי מידע רלוונטי.")
        
        score = ev.nodes[0].get_score()
        print(f"Top Score: {score:.4f}")
        
        if score < 0.35:
            return StopEvent(result="המידע שנמצא לא מספיק רלוונטי לשאלתך.")
        
        return ValidationEvent(nodes=ev.nodes, query=ev.query)

    @step
    async def generate(self, ctx: Context, ev: ValidationEvent) -> StopEvent:
        print("--- Step: Generation (Chat API) ---")
        llm = self.get_llm()
        context_str = "\n\n".join([n.get_content() for n in ev.nodes])
        
        messages = [
            ChatMessage(role="system", content="You are a professional assistant. Answer based ONLY on the context."),
            ChatMessage(role="user", content=f"Context:\n{context_str}\n\nQuestion: {ev.query}")
        ]
        
        try:
            response = await llm.achat(messages)
            return StopEvent(result=str(response.message.content))
        except Exception as e:
            return StopEvent(result=f"שגיאה: {str(e)}")

# --- הפונקציה שהייתה חסרה! ---
async def run_agent_query(user_query: str):
    wf = RAGWorkflow(timeout=60)
    result = await wf.run(query=user_query)
    return result