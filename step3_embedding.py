import os
from dotenv import load_dotenv
from llama_index.embeddings.cohere import CohereEmbedding

load_dotenv()

def get_embed_model():
    """מגדיר ומחזיר את מודל ה-Embedding של Cohere"""
    print("--- Step 3: Initializing Cohere embedding model ---")
    
    api_key = os.environ.get("COHERE_API_KEY")
    if not api_key:
        print("--- Step 3 Error: COHERE_API_KEY not found in .env ---")
        return None

    model = CohereEmbedding(
        api_key=api_key,
        model_name="embed-multilingual-v3.0",
        input_type="search_document"
    )
    print("--- Step 3: Model is ready ---")
    return model

if __name__ == "__main__":
    # בדיקה עצמאית של המודל
    model = get_embed_model()
    if model:
        test_vector = model.get_text_embedding("Hello world")
        print(f"Check: Vector generated with length {len(test_vector)}")