# ContextMesh

A 48-hour sprint to build a "Living Documentation" tool using Gemini 1.5 Pro's 2M context window.

## Architecture: "Lean Monolith"

- **Backend**: FastAPI (Python) - Handles ingestion and Gemini API interactions.
- **Frontend**: Next.js 15 (React) - Dashboard for visualization and chat.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Google Gemini API Key

## Setup

1.  **Clone/Open Repository**
    ```bash
    git clone <repo>
    cd contextmesh
    ```

2.  **Backend Setup**
    ```bash
    # Create virtual environment (optional but recommended)
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows

    # Install dependencies
    pip install -r backend/requirements.txt

    # Set API Key
    # Create a .env file in root or set env var
    # You can use either GOOGLE_API_KEY or GEMINI_API_KEY
    export GEMINI_API_KEY="your_key_here"
    ```

3.  **Frontend Setup**
    ```bash
    cd frontend
    npm install
    ```

## Running the App

1.  **Start Backend** (from root)
    ```bash
    uvicorn backend.main:app --reload --port 8000
    ```

2.  **Start Frontend** (from `frontend/`)
    ```bash
    npm run dev
    ```

3.  **Access**
    - Application: [http://localhost:3000](http://localhost:3000)
    - Backend Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
