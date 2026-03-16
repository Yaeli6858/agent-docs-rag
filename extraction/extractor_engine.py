import os
import ssl
import urllib3
import httpx
import json
from dotenv import load_dotenv
from typing import List
from llama_index.core import SimpleDirectoryReader
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.llms.cohere import Cohere

# ניסיון לייבוא הסכמה
try:
    from schema_definition import ExtractedProjectData
except ImportError:
    from .schema_definition import ExtractedProjectData

# --- 1. טעינת משתני סביבה ---
load_dotenv()

# --- 2. תיקון SSL לנטפרי ---
if "SSL_CERT_FILE" in os.environ:
    del os.environ["SSL_CERT_FILE"]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

def patched_init(self, *args, **kwargs):
    kwargs['verify'] = False
    return original_init(self, *args, **kwargs)

original_init = httpx.Client.__init__
httpx.Client.__init__ = patched_init
# -------------------------

def extract_structured_data(file_path: str):
    """מחלץ מידע מובנה מקובץ בודד"""
    print(f"--- Processing: {os.path.basename(file_path)} ---")
    
    documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
    content = documents[0].text
    
    api_key = os.environ.get("COHERE_API_KEY")
    llm = Cohere(api_key=api_key, model="command-r-08-2024")

    prompt_template_str = (
        "You are an expert developer. Extract technical insights from the text.\n"
        "Focus on: Technical Decisions, Coding Rules, and Security Warnings.\n"
        "Document Content:\n{content}\n"
    )

    program = LLMTextCompletionProgram.from_defaults(
        output_cls=ExtractedProjectData,
        prompt_template_str=prompt_template_str,
        llm=llm,
        verbose=False # נכבה את הפירוט המיותר כדי לראות פלט נקי
    )

    return program(content=content)

if __name__ == "__main__":
    # הנתיב שראיתי אצלך בהרצה הקודמת
    file_to_test = r".agentDocumentationRag\.github\instructions\general-copilot-instructions.md"
    
    if os.path.exists(file_to_test):
        try:
            print("--- Starting Test ---")
            res = extract_structured_data(file_to_test)
            print("\n✅ Successfully extracted data:")
            # שימוש ב-model_dump במקום json
            data_dict = res.model_dump()
            print(json.dumps(data_dict, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"❌ Error during execution: {e}")
    else:
        print(f"❌ File not found: {file_to_test}")