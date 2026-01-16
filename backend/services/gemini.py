import os
import datetime
from google import genai
from google.genai import types

# Constants
MODEL_NAME = "gemini-1.5-flash-001" # Switching to Flash for better availability

class GeminiService:
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            print("Warning: GOOGLE_API_KEY or GEMINI_API_KEY not set.")
        
        self.client = None
        self.cached_content_name = None
        
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Error initializing Gemini Client: {e}")
        else:
             print("Gemini Client not initialized (Missing API Key).")

    def create_cache(self, content_str: str, ttl_minutes: int = 600):
        """
        Create a cached content object in Gemini.
        """
        if not self.client:
            return

        try:
            print(f"Creating context cache via google.genai SDK (Length: {len(content_str)} chars)...")
            
            # Create the cache using the new SDK pattern
            # We treat the entire codebase as one big text for this sprint
            cache = self.client.caches.create(
                model=MODEL_NAME,
                config=types.CreateCachedContentConfig(
                    contents=[content_str],
                    ttl=f"{ttl_minutes}s", # SDK might expect string duration or seconds int depending on version
                )
            )
            
            self.cached_content_name = cache.name
            print(f"Cache created successfully: {self.cached_content_name}")

        except Exception as e:
            print(f"Failed to create cache: {e}")
            self.cached_content_name = None

    def analyze_codebase(self, context_xml: str, prompt: str, system_instruction: str):
        """
        Send the codebase + prompt to Gemini. Uses Cache if available.
        """
        try:
            if not self.client:
                 # Mock Response for Demonstration
                if "JSON" in system_instruction:
                    return """```json
{
  "summary": "### Mock Analysis (No API Key)\\n\\nSystem detected missing API Key. Returning simulated analysis.",
  "health_scores": [
    {"metric": "Modularity", "score": "A", "value": 90},
    {"metric": "Documentation", "score": "B", "value": 75},
    {"metric": "Test Coverage", "score": "C", "value": 45}
  ],
  "refactor_suggestions": [
     {"file": "backend/main.py", "issue": "Add Error Handling", "severity": "Medium"}
  ]
}
```"""
                return "Error: GOOGLE_API_KEY not set."

            # If we haven't cached yet, try to cache now (Lazy Caching)
            if not self.cached_content_name:
                self.create_cache(context_xml)

            # Prepare Request
            generation_config = None
            if "JSON" in system_instruction:
                generation_config = types.GenerateContentConfig(response_mime_type="application/json")

            # Use Cache if available
            if self.cached_content_name:
                print(f"Using Cached Content: {self.cached_content_name}")
                response = self.client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[prompt], # Context is in the cache
                    config=generation_config,
                    cached_content=self.cached_content_name # Pass the cache name
                )
            else:
                # Fallback to standard context window
                print("Cache not available. Sending full context.")
                full_prompt = [
                    system_instruction,
                    "Here is the codebase context:",
                    context_xml,
                    "--- End of Codebase ---",
                    "User Query:",
                    prompt
                ]
                response = self.client.models.generate_content(
                    model=MODEL_NAME,
                    contents=full_prompt,
                    config=generation_config
                )
            
            return response.text
        except Exception as e:
            return f"Error interacting with Gemini: {e}"

gemini_service = GeminiService()
