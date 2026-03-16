import os
import sys

# --- 1. ניקוי SSL אגרסיבי (חייב להופיע ראשון!) ---
# מוחק את הנתיב הבעייתי שגורם ל-FileNotFoundError
if "SSL_CERT_FILE" in os.environ:
    del os.environ["SSL_CERT_FILE"]

import ssl
import urllib3
import httpx

# עקיפת SSL גלובלית לנטפרי
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# הזרקה ל-httpx כדי שכל ספריה (כמו Gradio או Cohere) תעבוד בלי בדיקת תעודה
def patched_init(self, *args, **kwargs):
    kwargs['verify'] = False
    return original_init(self, *args, **kwargs)

original_init = httpx.Client.__init__
httpx.Client.__init__ = patched_init

# --- 2. עכשיו אפשר לייבא את שאר הספריות בביטחון ---
from dotenv import load_dotenv
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.cohere import Cohere
import gradio as gr

load_dotenv()

def start_rag_chat():
    print("--- Initializing RAG System (SSL Bypass Active) ---")
    
    # הגדרת מודל ה-Embeddings
    embed_model = CohereEmbedding(
        cohere_api_key=os.environ.get("COHERE_API_KEY"), 
        model_name="embed-multilingual-v3.0"
    )
    
    # הגדרת מודל השפה המעודכן
    llm = Cohere(
        api_key=os.environ.get("COHERE_API_KEY"), 
        model="command-r-08-2024" 
    )

    # חיבור ל-Pinecone
    pc = Pinecone(
        api_key=os.environ.get("PINECONE_API_KEY"), 
        ssl_verify=False
    )
    
    index_name = "code-docs-index"
    pinecone_index = pc.Index(index_name)
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    
    # טעינת האינדקס מהענן
    index = VectorStoreIndex.from_vector_store(
        vector_store, 
        embed_model=embed_model
    )
    
    query_engine = index.as_query_engine(llm=llm)

    def chat_function(message, history):
        try:
            # כאן המערכת שולפת מ-Pinecone ושולחת ל-Cohere
            response = query_engine.query(message)
            return str(response)
        except Exception as e:
            return f"שגיאה במערכת: {str(e)}"

    # יצירת הממשק
    ui = gr.ChatInterface(
        fn=chat_function,
        title="My Code RAG Chat",
        description="שאל אותי על הקוד שלך! (נטפרי bypass פעיל)",
    )
    
    print("--- RAG is Ready! הממשק עולה... ---")
    ui.launch(share=False)

if __name__ == "__main__":
    start_rag_chat()