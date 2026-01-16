from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from .gemini import gemini_service

# In-memory storage for events (for demonstration)
# In a real app, this would be a database
EVENTS_STORE = []

class WebhookPayload(BaseModel):
    action: str
    pull_request: Optional[Dict[str, Any]] = None
    repository: Optional[Dict[str, Any]] = None
    # For simulation/testing ease, we allow direct 'diff' injection
    diff: Optional[str] = None 

def process_github_webhook(payload: dict):
    """
    Process a GitHub-like webhook payload.
    Triggers 'The Architect' or 'The Refactorer' based on context.
    """
    event_id = len(EVENTS_STORE) + 1
    timestamp = datetime.now().isoformat()
    
    # Extract details
    action = payload.get("action", "unknown")
    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {})
    
    title = pr.get("title", "Unknown PR")
    user = pr.get("user", {}).get("login", "unknown_user")
    
    # Determine the "Diff" to analyze
    # In a real scenario, we'd use the PR URL or API to fetch the diff.
    # Here, we look for a 'diff' key in the top level (simulated) or just describe the PR.
    diff_content = payload.get("diff", "")
    
    if not diff_content and pr:
        diff_content = f"PR Title: {title}\nDescription: {pr.get('body', '')}"

    print(f"[{timestamp}] Processing Webhook: {action} on '{title}' by {user}")

    # Trigger Gemini
    # We use 'The Architect' to analyze the impact of this PR
    analysis_prompt = f"""
    A new Pull Request has been opened/updated:
    Title: {title}
    Author: {user}
    
    Diff/Context:
    {diff_content}
    
    Analyze the potential architectural impact of these changes. 
    Do they introduce new dependencies? 
    Do they follow existing patterns?
    """
    
    # We need the full codebase context for a true "ContextMesh" analysis
    # For now, we'll just pass the diff prompt, 
    # but in the 'Lean Monolith' vision, we would attach the cached codebase context too.
    # Let's assume gemini_service handles the context internally or we pass a placeholder.
    # Since we don't want to re-ingest the whole disk for every webhook in this MVP without caching:
    
    # TODO: Retrieve cached context ID if available
    
    gemini_response = gemini_service.analyze_codebase(
        context_xml="", # Passing empty context relying on Cache. If no cache, it might fail or need ingestion.
        prompt=analysis_prompt,
        system_instruction="You are The Architect. Analyze this PR."
    )
    
    event = {
        "id": event_id,
        "type": "webhook_pr",
        "timestamp": timestamp,
        "details": {
            "title": title,
            "user": user,
            "action": action
        },
        "analysis": gemini_response
    }
    
    EVENTS_STORE.append(event)
    return event

def get_recent_events(limit: int = 10):
    return sorted(EVENTS_STORE, key=lambda x: x['timestamp'], reverse=True)[:limit]
