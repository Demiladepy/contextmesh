from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.services.ingest import generate_xml_context
from backend.services.gemini import gemini_service
from backend.services.webhook import process_github_webhook, get_recent_events
import os

app = FastAPI(title="ContextMesh API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    repo_path: str = "."
    prompt: str
    agent_type: str = "architect" # architect, refactorer, documentarian

SYSTEM_PROMPTS = {
    "architect": """You are The Architect. 
Your goal is to analyze the codebase for high-level patterns, dependencies, and architectural health. 
Identify cross-module dependencies, circular imports, and potential scalability bottlenecks.

CRITICAL: You must output your response in JSON format.
Structure:
{
  "summary": "Markdown text summarizing the analysis...",
  "health_scores": [
    {"metric": "Modularity", "score": "A/B/C", "value": 85},
    {"metric": "Documentation", "score": "A/B/C", "value": 60},
    {"metric": "Test Coverage", "score": "A/B/C", "value": 75}
  ],
  "refactor_suggestions": [
    {"file": "path/to/file", "issue": "Short description", "severity": "High/Medium/Low"}
  ]
}
""",
    
    "refactorer": """You are The Refactorer.
Your goal is to identify technical debt, messy code, and areas that need improvement.
For each issue, provide a 'Refactor Plan' with specific 'Before' and 'After' code snippets.
Predict the impact of changes.
Output in Markdown.""",

    "documentarian": """You are The Documentarian.
Your goal is to generate a comprehensive README and "Living Documentation" for the codebase.
Focus on HOW the code works, not just what it is. Explain the flow of data and key architectural decisions."""
}

@app.post("/analyze")
async def analyze_repo(request: AnalysisRequest):
    # 1. Ingest Repo
    print(f"Ingesting repo at {request.repo_path}...")
    try:
        context_xml = generate_xml_context(request.repo_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    
    # 2. Select System Prompt
    system_prompt = SYSTEM_PROMPTS.get(request.agent_type.lower(), SYSTEM_PROMPTS["architect"])
    
    # 3. Call Gemini
    print(f"Sending to Gemini (Context Length: {len(context_xml)} chars)...")
    content = gemini_service.analyze_codebase(
        context_xml=context_xml, 
        prompt=request.prompt, 
        system_instruction=system_prompt
    )
    
    return {
        "agent": request.agent_type,
        "analysis": content
    }

# --- Webhook & Events ---

@app.post("/webhook")
async def receive_webhook(payload: dict):
    # Accepting raw dict to be flexible with GitHub's structure
    result = process_github_webhook(payload)
    return {"status": "processed", "event_id": result["id"]}

@app.get("/events")
async def events():
    return get_recent_events()

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
