from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import sqlite3

from services.openai_service import OpenAIService
from services.gemini_service import GeminiService

app = FastAPI(title="AICFO AI Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for prototype
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_system_settings():
    db_path = "../backend/database/database.sqlite"
    settings = {}
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM system_settings")
            for row in cursor.fetchall():
                settings[row['key']] = row['value']
            conn.close()
        except Exception as e:
            print(f"Error reading system settings DB: {e}")
    return settings

class ExtractionRequest(BaseModel):
    input_type: str
    text: Optional[str] = None
    audio_base64: Optional[str] = None
    client_timestamp: str
    user_context: Optional[dict] = None

@app.post("/internal/v1/extract/transaction")
async def extract_transaction(
    request: ExtractionRequest, 
    x_tenant_id: str = Header(None, description="The UUID of the active business")
):
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header is required")
        
    if request.input_type == "text" and request.text:
        transcript = request.text
    elif request.input_type == "audio" and request.audio_base64:
        # In a real app, send audio_base64 to Whisper STT here
        transcript = "Mock decoded audio transcript" 
    else:
        raise HTTPException(status_code=400, detail="Invalid input type or missing payload")

    settings = get_system_settings()
    is_enabled = settings.get("ai_enabled", "true") == "true"
    provider = settings.get("ai_provider", "mock")
    openai_key = settings.get("openai_api_key", "")
    gemini_key = settings.get("gemini_api_key", "")
    
    try:
        if not is_enabled:
            # Fallback to mock if deactivated
            os.environ["OPENAI_API_KEY"] = "mock-key"
            service = OpenAIService()
            result = service.extract_transaction_from_text(transcript, x_tenant_id, request.audio_base64)
        elif provider == "gemini" and len(gemini_key) > 10:
            service = GeminiService(api_key=gemini_key)
            result = service.extract_transaction_from_text(transcript, x_tenant_id, request.audio_base64, request.user_context)
        elif provider == "openai" and len(openai_key) > 10:
            os.environ["OPENAI_API_KEY"] = openai_key
            service = OpenAIService()
            result = service.extract_transaction_from_text(transcript, x_tenant_id, request.audio_base64)
        else:
            # Fallback to mock
            os.environ["OPENAI_API_KEY"] = "mock-key"
            service = OpenAIService()
            result = service.extract_transaction_from_text(transcript, x_tenant_id, request.audio_base64)
            
        return result
    except Exception as e:
        print(f"AI Provider Error: {e}")
        # Return a 500 status code with the actual error message so the UI can display it
        raise HTTPException(status_code=500, detail=f"AI Provider Error: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "aicfo-ai-service"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
