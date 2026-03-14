import os
import certifi
from dotenv import load_dotenv
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.groq import Groq # וודאי שהתקנת: pip install llama-index-llms-groq

# ייבוא מהתיקיות שבנינו
from app.chat_interface import create_ui
from core.rag_engine import setup_query_engine

# פתרון SSL לנטפרי
os.environ['SSL_CERT_FILE'] = certifi.where()
load_dotenv()

def start_app():
    print("🚀 Initializing Agent-Docs RAG Assistant 🚀")
    
    # 1. הגדרת מודל ה-Embedding (Cohere) - לצורך תרגום השאלה למספרים
    embed_model = CohereEmbedding(
        api_key=os.environ.get("COHERE_API_KEY"), 
        model_name="embed-multilingual-v3.0"
    )

    # 2. הגדרת ה-LLM (Groq) - ה"מוח" שמנסח את התשובה
    llm = Groq(
        model="llama3-70b-8192", 
        api_key=os.environ.get("GROQ_API_KEY")
    )
    
    # עדכון הגדרות גלובליות של LlamaIndex
    Settings.llm = llm
    Settings.embed_model = embed_model

    # 3. חיבור ל-Pinecone ושליפת האינדקס הקיים
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    pinecone_index = pc.Index("code-docs-index")
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    
    # יצירת אובייקט אינדקס מתוך מה ששמור כבר בענן
    index = VectorStoreIndex.from_vector_store(vector_store)

    # 4. הקמת מנוע השאילתות (עם הפרומפט שבנינו)
    engine = setup_query_engine(index, llm)

    # פונקציה שמקשרת בין ה-UI למנוע
    def ask_rag(question):
        print(f"User asked: {question}")
        response = engine.query(question)
        return str(response)

    # 5. הרצת ממשק Gradio
    print("--- Launching UI on http://127.0.0.1:7860 ---")
    ui = create_ui(ask_rag)
    ui.launch(share=False)

if __name__ == "__main__":
    start_app()