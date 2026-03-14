from llama_index.core import VectorStoreIndex

def create_index(nodes, storage_context, embed_model):
    """יוצר אינדקס מתוך ה-Nodes והגדרות האחסון"""
    print("--- Step 4: Indexing started ---")
    
    if not nodes:
        print("--- Step 4 Error: No nodes to index ---")
        return None

    # יצירת האינדקס - זה השלב שבו המידע נשלח ל-Cohere ול-Pinecone
    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True
    )
    
    print("--- Step 4: Indexing completed ---")
    return index