from llama_index.core.node_parser import SentenceSplitter

def split_to_nodes(documents):
    """מקבל רשימת מסמכים ומחזיר רשימת Nodes חתוכים"""
    if not documents:
        print("--- Step 2 Error: No documents provided to split ---")
        return []

    print("--- Step 2: Splitting documents into nodes ---")
    # הגדרת גודל החתיכות (512 טוקנים) וחפיפה ביניהן
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=20)
    nodes = splitter.get_nodes_from_documents(documents)
    
    print(f"--- Step 2: Created {len(nodes)} nodes ---")
    return nodes

if __name__ == "__main__":
    # בדיקה עצמאית (מייבא את שלב 1 כדי שיהיה מה לחתוך)
    from step1_loading import load_docs
    docs = load_docs()
    nodes = split_to_nodes(docs)
    if nodes:
        print(f"Check: First node content starts with: {nodes[0].get_content()[:50]}...")