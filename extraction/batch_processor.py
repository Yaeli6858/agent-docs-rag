# extraction/batch_processor.py
import os
import json
import sys
from dotenv import load_dotenv

# טעינת המפתח מה-.env
load_dotenv()

# מוודא שפייתון יודע לחפש קבצים בתוך תיקיית extraction
sys.path.append(os.path.dirname(__file__))

# ייבוא הפונקציה מהקובץ הקודם שיצרנו
try:
    from extractor_engine import extract_structured_data
except ImportError:
    from .extractor_engine import extract_structured_data

def run_batch_extraction():
    # 1. הגדרת נתיבים
    # שימי לב: זה הנתיב שבו נמצאים קבצי ה-md שלך
    docs_folder = r".agentDocumentationRag\.github\instructions"
    output_file = "project_knowledge.json" # הקובץ שייוצר בסוף
    
    print(f"--- Starting Batch Process ---")
    print(f"Looking for files in: {docs_folder}")

    # בדיקה אם התיקייה קיימת
    if not os.path.exists(docs_folder):
        print(f"❌ Error: Folder not found at {docs_folder}")
        return

    # 2. הכנת המבנה הריק שנמלא במידע
    all_project_data = {
        "decisions": [],
        "rules": [],
        "warnings": []
    }

    # 3. מציאת כל קבצי ה-Markdown בתיקייה
    files = [f for f in os.listdir(docs_folder) if f.endswith('.md')]
    print(f"Found {len(files)} files to process.")

    # 4. מעבר על כל קובץ וחילוץ המידע
    for file_name in files:
        file_path = os.path.join(docs_folder, file_name)
        try:
            # קריאה למנוע ה-AI שבנינו בשיעור הקודם
            extracted_data = extract_structured_data(file_path)
            
            # הוספת המידע שחולץ לרשימות המרכזיות שלנו
            # אנחנו משתמשים ב-model_dump() כי זה אובייקט Pydantic
            all_project_data["decisions"].extend([d.model_dump() for d in extracted_data.decisions])
            all_project_data["rules"].extend([r.model_dump() for r in extracted_data.rules])
            all_project_data["warnings"].extend([w.model_dump() for w in extracted_data.warnings])
            
            print(f"✅ Finished processing: {file_name}")
        except Exception as e:
            print(f"❌ Error processing {file_name}: {e}")

    # 5. שמירת הכל לקובץ JSON אחד גדול
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_project_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✨ SUCCESS! Created database file: {output_file}")

if __name__ == "__main__":
    run_batch_extraction()