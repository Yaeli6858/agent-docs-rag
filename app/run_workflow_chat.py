import os
import sys

# --- 1. ניקוי SSL אגרסיבי (חייב להופיע ראשון, לפני כל import אחר!) ---
if "SSL_CERT_FILE" in os.environ:
    del os.environ["SSL_CERT_FILE"]

# --- 2. ייבוא ספריות התקשורת והתצוגה ---
import ssl
import urllib3
import httpx
import asyncio
import gradio as gr
from dotenv import load_dotenv

# --- 3. הגדרות עקיפת SSL לנטפרי ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

def patched_init(self, *args, **kwargs):
    kwargs['verify'] = False
    return original_init(self, *args, **kwargs)

original_init = httpx.Client.__init__
httpx.Client.__init__ = patched_init

# תיקון גם לגרסה האסינכרונית (חשוב ל-Workflow)
original_async_init = httpx.AsyncClient.__init__
def patched_async_init(self, *args, **kwargs):
    kwargs['verify'] = False
    return original_async_init(self, *args, **kwargs)
httpx.AsyncClient.__init__ = patched_async_init

# --- 4. טעינת הגדרות וייבוא המנועים שלנו ---
load_dotenv()

# הוספת תיקיית השורש לנתיב כדי למצוא את extraction ו-core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.workflow_engine import run_agent_query
from extraction.smart_router import ProjectRouter

# יצירת מופע של הנתב (Router)
router = ProjectRouter()

# --- 5. הגדרת ממשק המשתמש ---

async def chat_function(message, history):
    """הפונקציה המרכזית שמנהלת את השיחה ומחליטה על הנתיב"""
    try:
        print(f"--- Query Received: {message} ---")
        
        # שלב א: ה-Router מחליט אם זו שאלה על חוקים (JSON) או מידע כללי (Pinecone)
        route = router.decide_route(message)
        print(f"--- Router Decision: {route} ---")
        
        if route == "structured":
            # שליפה מהקובץ המובנה (JSON)
            response = router.ask_from_json(message)
            return f"📋 **[מתוך חוקי הפרויקט]:**\n\n{response}"
        
        else:
            # הפעלת ה-Workflow הסמנטי (Pinecone)
            response = await run_agent_query(message)
            return str(response)

    except Exception as e:
        print(f"❌ Error: {e}")
        return f"מצטער, קרתה שגיאה בתהליך: {str(e)}"

def start_ui():
    """מפעיל את Gradio"""
    demo = gr.ChatInterface(
        fn=chat_function,
        title="🤖 Hybrid RAG System",
        description="מערכת חכמה המשלבת חיפוש סמנטי (Pinecone) עם שליפת חוקים מובנים (JSON).",
        examples=[
            "אילו חוקי קידוד קיימים ב-Services?",
            "איך עובד תהליך ה-Auth בפרויקט?",
            "תביא לי סיכום של האזהרות הטכניות."
        ]
            )
    
    print("🚀 Gradio is starting...")
    demo.launch(share=False)

if __name__ == "__main__":
    start_ui()