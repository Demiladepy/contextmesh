# ContextMesh 🕸️

**Living Documentation & Code Analysis Powered by Gemini 1.5 Pro**

ContextMesh is a cutting-edge "Lean Monolith" application designed to bridge the gap between code and documentation. Leveraging the massive 2M token context window of Google's Gemini 1.5 Pro, it ingests entire repositories to provide holistic analysis, refactoring advice, and automated documentation.

---

##  The Agents

ContextMesh exposes three distinct AI personas to interact with your codebase:

###  The Architect
Analyzes high-level patterns, dependencies, and architectural health.
- Identifies circular imports and scalability bottlenecks.
- Generates "Health Scores" for Modularity, Documentation, and Test Coverage.

###  The Refactorer
Your dedicated technical debt collector.
- Identifies messy code and anti-patterns.
- Provides specific "Before" and "After" refactoring plans.
- Predicts the impact of proposed changes.

###  The Documentarian
Turns code into plain English.
- Generates comprehensive READMEs and "Living Documentation".
- Explains data flow and key architectural decisions, not just syntax.

---

##  Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **AI Model**: Google Gemini 1.5 Pro (via `google-genai`)
- **Utilities**: `pathspec` (gitignore handling), `pydantic` (validation)
- **Integration**: GitHub Webhooks

### Frontend
- **Framework**: [Next.js 16](https://nextjs.org/) (App Router)
- **Library**: React 19
- **Styling**: Tailwind CSS v4
- **Icons**: Lucide React

---

##  Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- A Google Cloud Project with Gemini API enabled ([Get API Key](https://aistudio.google.com/))

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/contextmesh.git
    cd contextmesh
    ```

2.  **Backend Setup**
    ```bash
    # It is recommended to use a virtual environment
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate

    # Install Python dependencies
    pip install -r backend/requirements.txt

    # Set your API Key
    # Linux/Mac
    export GEMINI_API_KEY="your_actual_api_key_here"
    # Windows (PowerShell)
    $env:GEMINI_API_KEY="your_actual_api_key_here"
    ```
    *(Alternatively, create a `.env` file in the root directory)*

3.  **Frontend Setup**
    ```bash
    cd frontend
    npm install
    ```

---

##  Running the Application

You will need two terminal windows to run the full stack.

### 1. Start the Backend API
From the project root:
```bash
uvicorn backend.main:app --reload --port 8000
```
- **API URL**: [http://localhost:8000](http://localhost:8000)
- **Interactive Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Start the Frontend Dashboard
From the `frontend/` directory:
```bash
npm run dev
```
- **Dashboard**: [http://localhost:3000](http://localhost:3000)

---

##  API Endpoints

- `POST /analyze`: Main endpoint to trigger an agent (Architect, Refactorer, Documentarian) on a local path.
- `POST /webhook`: Webhook receiver for GitHub events.
- `GET /events`: Fetch recent webhook events.
