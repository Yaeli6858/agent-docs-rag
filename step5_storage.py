import os
from pinecone import Pinecone

def verify_pinecone():
    """בודק כמה וקטורים יש ב-Pinecone כרגע"""
    print("--- Step 5: Verifying Pinecone storage ---")
    
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    index_name = "code-docs-index"
    
    pinecone_index = pc.Index(index_name)
    stats = pinecone_index.describe_index_stats()
    
    count = stats['total_vector_count']
    print(f"--- Step 5 Check: Total vectors in Pinecone: {count} ---")
    return count

if __name__ == "__main__":
    verify_pinecone()