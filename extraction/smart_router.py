# extraction/smart_router.py
import os
import json
import ssl
import urllib3
import httpx
from dotenv import load_dotenv
from llama_index.llms.cohere import Cohere
from llama_index.core.base.llms.types import ChatMessage

load_dotenv()

# --- תיקון SSL לנטפרי ---
if "SSL_CERT_FILE" in os.environ: del os.environ["SSL_CERT_FILE"]
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context
def patched_init(self, *args, **kwargs):
    kwargs['verify'] = False
    return original_init(self, *args, **kwargs)
original_init = httpx.Client.__init__
httpx.Client.__init__ = patched_init
# -------------------------

class ProjectRouter:
    def __init__(self):
        self.llm = Cohere(api_key=os.environ.get("COHERE_API_KEY"), model="command-r-08-2024")
        self.knowledge_file = "project_knowledge.json"

    def decide_route(self, query):
        """מחליט האם ללכת ל-JSON או ל-Pinecone"""
        prompt = f"""
        Classify the user query into one of two categories:
        1. 'structured': Use this if the user asks for lists of rules, coding standards, warnings, or a summary of technical decisions.
        2. 'semantic': Use this for general questions, explaining concepts, or "how-to" questions.
        
        Query: {query}
        Response (one word only: structured or semantic):"""
        
        response = self.llm.chat(messages=[ChatMessage(role="user", content=prompt)])
        decision = str(response.message.content).strip().lower()
        return "structured" if "structured" in decision else "semantic"

    def ask_from_json(self, question):
        """שליפת תשובה מה-JSON"""
        if not os.path.exists(self.knowledge_file): return "קובץ הידע חסר."
        with open(self.knowledge_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        content = f"Base your answer ONLY on this JSON: {json.dumps(data, ensure_ascii=False)}\nQuestion: {question}\nAnswer in Hebrew:"
        response = self.llm.chat(messages=[ChatMessage(role="user", content=content)])
        return str(response.message.content)