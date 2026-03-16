# extraction/schema_definition.py
from pydantic import BaseModel, Field
from typing import List

# הגדרת מבנה עבור החלטה טכנית
class TechnicalDecision(BaseModel):
    title: str = Field(description="כותרת קצרה של ההחלטה")
    summary: str = Field(description="תמצית ההחלטה הטכנית שנלקחה")
    tags: List[str] = Field(description="תגיות רלוונטיות (למשל: db, backend, auth)")
    source_file: str = Field(description="שם הקובץ ממנו נלקח המידע")

# הגדרת מבנה עבור כלל קידוד
class CodingRule(BaseModel):
    rule: str = Field(description="הנחיית הקידוד או הסטנדרט הנדרש")
    scope: str = Field(description="היכן הכלל תקף (למשל: Controllers, Services, Frontend)")
    severity: str = Field(description="מידת החשיבות: Mandatory / Recommendation")

# הגדרת מבנה עבור אזהרת אבטחה
class SecurityWarning(BaseModel):
    area: str = Field(description="האזור המערכתי הרלוונטי לאזהרה")
    message: str = Field(description="פירוט האזהרה")
    mitigation: str = Field(description="איך למנוע את הבעיה לפי המסמך")

# המכולה הראשית שמאגדת הכל
class ExtractedProjectData(BaseModel):
    decisions: List[TechnicalDecision]
    rules: List[CodingRule]
    warnings: List[SecurityWarning]