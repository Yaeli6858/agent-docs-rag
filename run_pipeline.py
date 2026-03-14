import os
import certifi
from dotenv import load_dotenv
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import StorageContext

# פתרון SSL לנטפרי
os.environ['SSL_CERT_FILE'] = certifi.where()
load_dotenv()

# ייבוא השלבים שיצרנו
import step1_loading as s1
import step2_chunking as s2
import step3_embedding as s3
import step4_indexing as s4
import step5_storage as s5

def run():
    print("=== Starting RAG Pipeline ===")

    # 1. Loading
    docs = s1.load_docs()
    if not docs: return

    # 2. Chunking
    nodes = s2.split_to_nodes(docs)
    if not nodes: return

    # 3. Embedding Setup
    embed_model = s3.get_embed_model()
    if not embed_model: return

    # הכנת החיבור לפינקורן עבור שלב 4
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    pinecone_index = pc.Index("code-docs-index")
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 4. Indexing (The actual upload)
    s4.create_index(nodes, storage_context, embed_model)

    # 5. Verification
    s5.verify_pinecone()

    print("=== Pipeline Finished Successfully ===")

if __name__ == "__main__":
    run()