import os
import certifi
import urllib3
import ssl
import httpx # <--- חשוב לוודא שזה מותקן
from dotenv import load_dotenv
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import StorageContext

# 1. ביטול אזהרות SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. התיקון האולטימטיבי לנטפרי - עקיפת SSL גלובלית
ssl._create_default_https_context = ssl._create_unverified_context

# 3. פתרון ספציפי לספריית httpx (שמשמשת את Cohere)
# אנחנו יוצרים "לקוח" שלא בודק SSL ומגדירים אותו כברירת מחדל
def patched_init(self, *args, **kwargs):
    kwargs['verify'] = False
    return original_init(self, *args, **kwargs)

original_init = httpx.Client.__init__
httpx.Client.__init__ = patched_init

# 4. הגדרות סביבה
os.environ['SSL_CERT_FILE'] = certifi.where()
load_dotenv()

# ייבוא השלבים
from data_pipeline import step1_loading as s1
from data_pipeline import step2_chunking as s2
from data_pipeline import step3_embedding as s3
from data_pipeline import step4_indexing as s4
from data_pipeline import step5_storage as s5

def run():
    print("=== Starting RAG Pipeline ===")

    # טעינה וחיתוך
    docs = s1.load_docs()
    if not docs: return

    nodes = s2.split_to_nodes(docs)
    if not nodes: return

    embed_model = s3.get_embed_model()
    if not embed_model: return

    # חיבור לפינקורן
    print("--- Step 4: Connecting to Pinecone ---")
    pc = Pinecone(
        api_key=os.environ.get("PINECONE_API_KEY"),
        ssl_verify=False 
    )
    
    pinecone_index = pc.Index("code-docs-index")
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 4. העלאה (עכשיו גם Cohere יעבור בשלום)
    print(f"--- Step 4: Uploading {len(nodes)} nodes to Cloud ---")
    s4.create_index(nodes, storage_context, embed_model)

    # 5. אימות סופי
    s5.verify_pinecone()

    print("=== ✅ Pipeline Finished Successfully ===")

if __name__ == "__main__":
    run()