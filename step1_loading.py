import os
import certifi
from llama_index.core import SimpleDirectoryReader

# הגדרת אישורים לנטפרי
os.environ['SSL_CERT_FILE'] = certifi.where()

def load_docs():
    """טוען מסמכים מהתיקייה ומחזיר רשימת Documents"""
    print("--- Step 1: Loading documents started ---")
    base_path = "./.agentDocumentationRag"
    
    if not os.path.exists(base_path):
        print(f"--- Error: Directory {base_path} not found ---")
        return []

    # טעינה כולל תיקיות נסתרות (עבור קורסור וגיטהאב)
    reader = SimpleDirectoryReader(
        input_dir=base_path, 
        recursive=True, 
        exclude_hidden=False
    )
    documents = reader.load_data()
    print(f"--- Step 1: Loaded {len(documents)} documents successfully ---")
    return documents

if __name__ == "__main__":
    # מאפשר להריץ את הקובץ לבד לבדיקה
    docs = load_docs()
    if docs:
        print(f"Check: First file name is {docs[0].metadata.get('file_name')}")