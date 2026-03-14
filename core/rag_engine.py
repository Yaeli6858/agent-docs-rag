import os
from llama_index.core import PromptTemplate
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.retrievers import VectorIndexRetriever

def setup_query_engine(index, llm):
    """
    Setup the RAG engine with a custom prompt and Groq LLM.
    """
    print("--- Core: Configuring Query Engine with Custom Prompt ---")
    
    # 1. הגדרת הפרומפט - מנחה את ה-AI איך להתנהג
    template = (
        "You are a professional technical assistant. Your goal is to answer questions "
        "based ONLY on the provided context from coding agent documentation.\n"
        "If the answer is not in the context, clearly state that you don't know.\n"
        "Always try to mention which file the information came from.\n\n"
        "Context information is below:\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Given the context information and not prior knowledge, "
        "answer the query.\n"
        "Query: {query_str}\n"
        "Answer: "
    )
    qa_template = PromptTemplate(template)

    # 2. הגדרת השליפה (Retriever)
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=3,
    )

    # 3. יצירת המנוע שמשלב הכל
    query_engine = RetrieverQueryEngine.from_args(
        retriever=retriever,
        node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
        text_qa_template=qa_template,
        llm=llm  # כאן אנחנו מזריקים את Groq
    )
    
    print("--- Core: Query Engine is ready ---")
    return query_engine