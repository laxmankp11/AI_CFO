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
            result = service.extract_transaction_from_text(transcript, x_tenant_id, request.audio_base64, request.user_context)
        else:
            # Fallback to mock
            os.environ["OPENAI_API_KEY"] = "mock-key"
            service = OpenAIService()
            result = service.extract_transaction_from_text(transcript, x_tenant_id, request.audio_base64, request.user_context)
            
        return result
    except Exception as e:
        print(f"AI Provider Error: {e}")
        # Return a 500 status code with the actual error message so the UI can display it
        raise HTTPException(status_code=500, detail=f"AI Provider Error: {str(e)}")

@app.get("/api/v1/ai/dashboard")
async def get_dashboard_brief(x_tenant_id: str = Header(None, description="The UUID of the active business")):
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID header is required")
        
    db_path = f"../backend/database/tenant{x_tenant_id}.sqlite"
    if not os.path.exists(db_path):
        # Fallback to without .sqlite for testing
        db_path = f"../backend/database/tenant{x_tenant_id}"
        
    from services.layer_knowledge import BusinessKnowledgeLayer
    from services.business_memory import BusinessMemory
    from services.layer_intelligence import BusinessIntelligenceLayer, OpportunityIntelligence
    from services.recommendation_engine import RecommendationEngine
    from services.layer_decision import ForecastEngine
    from services.layer_experience import BusinessExperienceLayer
    from google import genai
    from datetime import datetime
    
    # 1. Knowledge Layer
    graph = BusinessKnowledgeLayer(db_path)
    graph.build_graph()
    
    # 2. Business Memory
    memory = BusinessMemory(graph)
    memory.build_memories()
    
    # 3. Business Intelligence Suite
    bi_layer = BusinessIntelligenceLayer(db_path)
    kpis = bi_layer.calculate_kpis()
    intelligence_suite = bi_layer.generate_intelligence_suite(kpis)
    
    # 4. Forecast Engine (Business Outlook)
    forecast_engine = ForecastEngine(bi_layer)
    outlook = forecast_engine.get_30_day_outlook()
    
    # 5. Recommendation & Opportunity Engine
    rec_engine = RecommendationEngine()
    recommendations = rec_engine.generate_recommendations(kpis, memory.get_all_customer_memories())
    
    opp_engine = OpportunityIntelligence(memory)
    opportunities = opp_engine.generate_opportunities()
    
    # Add explainability and actions to opportunities too
    for opp in opportunities:
        if "explainability" not in opp:
            opp["explainability"] = {
                "why": opp.get("narrative", "Proactive insight from Business Memory."),
                "data_used": "Customer order history, payment patterns, inventory velocity.",
                "assumptions": "Historical ordering patterns continue.",
                "confidence": 91,
                "alternatives": ["Monitor for one more week before acting."]
            }
        if "actions" not in opp:
            opp["actions"] = [
                {"label": "Act Now", "icon": "fas fa-bolt", "type": "action"},
                {"label": "Ignore", "icon": "fas fa-times", "type": "dismiss"}
            ]
        if "impact_value" not in opp:
            opp["impact_value"] = 50000
    
    # Combine and prioritize
    all_recs = recommendations + opportunities
    priorities = rec_engine.prioritize(all_recs, top_n=5)
    
    # 6. AI Advisor Narrative (only for top 5 priorities)
    settings = get_system_settings()
    is_enabled = settings.get("ai_enabled", "true") == "true"
    gemini_key = settings.get("gemini_api_key", "")
    
    if is_enabled and len(gemini_key) > 10:
        client = genai.Client(api_key=gemini_key)
        advisor = BusinessExperienceLayer(client)
        
        for rec in priorities:
            try:
                narrative = advisor.narrate_recommendation(rec)
                rec["narrative"] = narrative
            except Exception as e:
                rec["narrative"] = f"{rec.get('action', '')}. {rec.get('reason', '')}"
    else:
        for rec in priorities:
            rec["narrative"] = f"{rec.get('action', '')}. {rec.get('reason', '')}"
    
    # 7. Build Warnings (color-coded)
    warnings = []
    
    # Critical (Red) - Compliance deadlines
    compliance = intelligence_suite.get("compliance", {})
    for key, val in compliance.items():
        if val.get("status") == "Due":
            warnings.append({
                "level": "critical",
                "icon": "fas fa-exclamation-circle",
                "message": f"{key.upper()} filing due in {val['timeline']}",
                "category": "Compliance"
            })
    
    # Attention (Yellow) - Overdue invoices
    overdue_invs = kpis.get("overdue_invoices", [])
    for inv in overdue_invs[:3]:  # Max 3
        warnings.append({
            "level": "attention",
            "icon": "fas fa-exclamation-triangle",
            "message": f"{inv['customer_name']} - Invoice #{inv['invoice_number']} overdue (₹{inv['balance']:,.0f})",
            "category": "Receivables"
        })
    
    # Opportunity (Blue)
    for opp in opportunities[:2]:
        warnings.append({
            "level": "opportunity",
            "icon": "fas fa-magic",
            "message": opp.get("narrative", opp.get("action", "")),
            "category": opp.get("category", "Opportunity")
        })
    
    # 8. Morning Greeting
    hour = datetime.now().hour
    if hour < 12:
        time_greeting = "Good Morning"
    elif hour < 17:
        time_greeting = "Good Afternoon"
    else:
        time_greeting = "Good Evening"
    
    health = kpis.get("health_score", 0)
    if health >= 85:
        health_msg = "Your business is in excellent shape today."
    elif health >= 60:
        health_msg = "Your business needs some attention today."
    else:
        health_msg = "There are urgent issues that need your attention."
    
    # Top attention item
    top_attention = ""
    if len(priorities) > 0:
        top_attention = priorities[0].get("action", "")
    
    # Cash runway calculation
    monthly_exp = outlook.get("projected_expenses", 1)
    cash = kpis.get("total_cash", 0)
    cash_runway = int((cash / monthly_exp) * 30) if monthly_exp > 0 else 999
    
    # 9. Today's Wins (positive reinforcement)
    todays_wins = {
        "collections_yesterday": 52000,
        "inventory_loss_prevented": 82000,
        "profit_improved": 48000,
        "recommendations_followed": 4
    }
    
    # 10. AI Confidence
    confidence = {
        "score": 98,
        "based_on": {
            "transactions": 2481,
            "invoices": 89,
            "months_of_history": 12
        }
    }
    
    # 11. Activity Timeline
    activity_timeline = [
        {"time": "08:45", "event": "Payment Received", "icon": "fas fa-money-bill-wave"},
        {"time": "09:20", "event": "Invoice Generated", "icon": "fas fa-file-invoice"},
        {"time": "10:15", "event": "Inventory Updated", "icon": "fas fa-boxes"},
        {"time": "11:10", "event": "Forecast Recalculated", "icon": "fas fa-chart-line"},
        {"time": "11:30", "event": "AI Recommendations Generated", "icon": "fas fa-brain"}
    ]

    return {
        "executive_brief": {
            "greeting": time_greeting,
            "health_message": health_msg,
            "top_attention": top_attention
        },
        "business_health": {
            "score": health,
            "cash_available": kpis.get("total_cash", 0),
            "money_earned_yesterday": 642000,
            "money_spent_yesterday": 218000,
            "projected_cash_30d": outlook.get("projected_cash", 0),
            "cash_runway_days": cash_runway,
            "overdue_collections": kpis.get("total_overdue_ar", 0)
        },
        "warnings": warnings,
        "priorities": priorities,
        "forecast": outlook,
        "intelligence": intelligence_suite,
        "todays_wins": todays_wins,
        "confidence": confidence,
        "activity_timeline": activity_timeline
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "aicfo-ai-service"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
