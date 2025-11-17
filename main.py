import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

from database import db, create_document, get_documents
from schemas import Sector, Tool, Comparison

app = FastAPI(title="AI Tools Blog API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AI Tools Blog Backend Running"}

@app.get("/schema")
def get_schema():
    """Expose Pydantic schema models for the DB viewer."""
    return {
        "sector": Sector.model_json_schema(),
        "tool": Tool.model_json_schema(),
        "comparison": Comparison.model_json_schema(),
    }

@app.get("/test")
def test_database():
    """Test endpoint to check database connectivity and collections"""
    response: Dict[str, Any] = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response

# Seed some starter sectors and comparisons if not present
@app.post("/seed")
def seed_content():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    existing_sectors = list(db["sector"].find({}))
    if not existing_sectors:
        sectors = [
            Sector(name="Marketing", slug="marketing", description="Campaigns, content, SEO"),
            Sector(name="Sales", slug="sales", description="Prospecting and enablement"),
            Sector(name="Customer Support", slug="support", description="Helpdesk and chatbots"),
            Sector(name="Software Development", slug="engineering", description="Code assistants and DevOps"),
            Sector(name="Design", slug="design", description="Images, video, UI/UX")
        ]
        for s in sectors:
            create_document("sector", s)

    existing_tools = list(db["tool"].find({}))
    if not existing_tools:
        tools = [
            Tool(name="Jasper", sector_slug="marketing", summary="AI copy for ads and blogs", strengths=["Templates", "Brand voice"], limitations=["Price"], website="https://www.jasper.ai", pricing="From $39/mo", rating=4.2),
            Tool(name="HubSpot AI", sector_slug="marketing", summary="AI features inside HubSpot", strengths=["Integrated"], limitations=["Ecosystem lock-in"], website="https://www.hubspot.com", pricing="Tiered", rating=4.0),
            Tool(name="Apollo AI", sector_slug="sales", summary="Prospecting with AI signals", strengths=["Data"], limitations=["Learning curve"], website="https://www.apollo.io", pricing="Freemium", rating=4.3),
            Tool(name="Gong", sector_slug="sales", summary="Revenue intelligence", strengths=["Call analysis"], limitations=["Enterprise pricing"], website="https://www.gong.io", pricing="Quote-based", rating=4.5),
            Tool(name="Intercom Fin", sector_slug="support", summary="AI chatbot for support", strengths=["Answers from docs"], limitations=["Requires good KB"], website="https://www.intercom.com", pricing="Add-on", rating=4.4),
            Tool(name="Zendesk AI", sector_slug="support", summary="AI assist in helpdesk", strengths=["Workflows"], limitations=["Add-on cost"], website="https://www.zendesk.com", pricing="Add-on", rating=4.1),
            Tool(name="GitHub Copilot", sector_slug="engineering", summary="Code completion and chat", strengths=["IDE integration"], limitations=["Best with popular langs"], website="https://github.com/features/copilot", pricing="$10-$19/mo", rating=4.7),
            Tool(name="OpenAI o1", sector_slug="engineering", summary="Reasoning models for complex tasks", strengths=["Reasoning"], limitations=["Cost"], website="https://openai.com", pricing="Usage-based", rating=4.6),
            Tool(name="Midjourney", sector_slug="design", summary="Generative images", strengths=["Quality"], limitations=["Discord UX"], website="https://www.midjourney.com", pricing="From $10/mo", rating=4.6),
            Tool(name="Figma AI", sector_slug="design", summary="Generate and edit UI", strengths=["Design-native"], limitations=["Early features"], website="https://www.figma.com", pricing="Included", rating=4.2)
        ]
        for t in tools:
            create_document("tool", t)

    existing_comparisons = list(db["comparison"].find({}))
    if not existing_comparisons:
        comps = [
            Comparison(sector_slug="marketing", headline="Best AI Tools for Marketing in 2025", intro="We tested top tools for content, SEO, and campaigns.", top_tools=["Jasper", "HubSpot AI"]),
            Comparison(sector_slug="sales", headline="Top AI Tools for Sales Teams", intro="Prospecting, call analysis, and forecasting.", top_tools=["Gong", "Apollo AI"]),
            Comparison(sector_slug="support", headline="AI for Customer Support", intro="Bots, deflection, and agent assistance.", top_tools=["Intercom Fin", "Zendesk AI"]),
            Comparison(sector_slug="engineering", headline="AI for Software Development", intro="Code completion, reviews, and reasoning.", top_tools=["GitHub Copilot", "OpenAI o1"]),
            Comparison(sector_slug="design", headline="AI for Designers", intro="From ideas to assets.", top_tools=["Midjourney", "Figma AI"])        
        ]
        for c in comps:
            create_document("comparison", c)

    return {"status": "ok"}

# Public read endpoints
@app.get("/sectors")
def list_sectors():
    docs = get_documents("sector") if db else []
    return [{"id": str(d.get("_id")), "name": d.get("name"), "slug": d.get("slug"), "description": d.get("description")} for d in docs]

@app.get("/sectors/{slug}")
def sector_detail(slug: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    sector = db["sector"].find_one({"slug": slug})
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")
    tools = list(db["tool"].find({"sector_slug": slug}))
    comparison = db["comparison"].find_one({"sector_slug": slug})
    return {
        "sector": {"name": sector.get("name"), "slug": sector.get("slug"), "description": sector.get("description")},
        "tools": [
            {
                "name": t.get("name"),
                "summary": t.get("summary"),
                "strengths": t.get("strengths", []),
                "limitations": t.get("limitations", []),
                "website": t.get("website"),
                "pricing": t.get("pricing"),
                "rating": t.get("rating"),
            } for t in tools
        ],
        "comparison": comparison and {
            "headline": comparison.get("headline"),
            "intro": comparison.get("intro"),
            "top_tools": comparison.get("top_tools", [])
        }
    }

# Simple search endpoint
class SearchQuery(BaseModel):
    q: str

@app.post("/search")
def search_tools(query: SearchQuery):
    if db is None:
        return {"results": []}
    pattern = {"$regex": query.q, "$options": "i"}
    tools = list(db["tool"].find({"$or": [{"name": pattern}, {"summary": pattern}, {"sector_slug": pattern}]}))
    return {"results": [
        {
            "name": t.get("name"),
            "sector_slug": t.get("sector_slug"),
            "summary": t.get("summary"),
            "rating": t.get("rating"),
            "website": t.get("website"),
        } for t in tools
    ]}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
