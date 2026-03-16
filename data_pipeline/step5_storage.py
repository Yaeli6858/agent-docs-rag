import os
from pinecone import Pinecone

def verify_pinecone():
    print("--- Step 5: Verifying Pinecone storage ---")
    
    # חיבור עם עקיפת SSL עבור נטפרי
    pc = Pinecone(
        api_key=os.environ.get("PINECONE_API_KEY"),
        ssl_verify=False
    )
    
    index_name = "code-docs-index"
    index = pc.Index(index_name)
    
    # בדיקת סטטיסטיקות
    stats = index.describe_index_stats()
    total_vectors = stats['total_vector_count']
    
    print(f"✅ Verification successful!")
    print(f"📊 Total vectors in index '{index_name}': {total_vectors}")
    
    if total_vectors > 0:
        print("🚀 Data is ready for chatting!")
    else:
        print("⚠️ Warning: Index is empty. Something went wrong during upload.")