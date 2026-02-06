Create a Python FastAPI + Streamlit project for a "Virtual Department Representatives" system for a hackathon.

PROJECT STRUCTURE:
- Backend: FastAPI with SQLAlchemy and SQLite
- Frontend: Streamlit
- LLM: Ollama (local inference)
- Two separate entry points: API server + Streamlit app

REQUIREMENTS:

1. PROJECT SETUP:
   - Initialize project with proper directory structure:
     /backend (FastAPI)
     /frontend (Streamlit)
     /shared (shared models, utilities)
   - Create requirements.txt with: fastapi, uvicorn, sqlalchemy, python-multipart, ollama, pypdf2, streamlit, requests
   - Create .env file for configuration
   - Add .gitignore for Python projects

2. DATABASE MODELS (shared/models.py):
   - Document model with fields: id, title, content, upload_date, tags (JSON string), metadata
   - Use SQLAlchemy ORM with SQLite
   - SQLite database file: data/knowledge.db

3. PERSONA SYSTEM (shared/personas.py):
   - Define 6 department personas with system prompts:
     * Engineering: Technical, detailed, architecture-focused
     * Delivery: Action-oriented, timelines, deliverables  
     * Admin: Process-focused, organizational
     * Sales: Client-centric, business outcomes
     * C-level: Strategic, high-level, risks/opportunities
     * Marketing: Campaign-focused, storytelling, past projects

4. BACKEND API ENDPOINTS (backend/main.py):
   - POST /upload/document - Upload and parse text/PDF files
   - POST /chat - Query with department parameter
   - GET /departments - List all available departments
   - GET /documents - List uploaded documents
   - DELETE /documents/{id} - Delete document
   - GET /health - Health check
   - Enable CORS for Streamlit frontend

5. OLLAMA INTEGRATION (backend/llm.py):
   - Function to call Ollama with persona + context + query
   - Use llama3.2 model (or mistral as fallback)
   - Error handling for when Ollama is not running
   - Context assembly: fetch recent documents and format for LLM

6. DOCUMENT PROCESSING (backend/document_processor.py):
   - Parse .txt, .md, .pdf files
   - Extract text content
   - Store in SQLite database
   - Handle file upload from FastAPI

7. STREAMLIT FRONTEND (frontend/app.py):
   - Page title and description
   - Sidebar with 6 department buttons (use st.sidebar.radio or buttons)
   - Main area with:
     * File upload widget (st.file_uploader) for documents
     * Chat input (st.chat_input)
     * Chat message display (st.chat_message)
     * Document list viewer (expandable section)
   - Session state to maintain chat history per department
   - Make API calls to FastAPI backend using requests library
   - Add loading spinners while waiting for LLM response

8. DATABASE INITIALIZATION (backend/database.py):
   - SQLite connection setup
   - Create tables on startup
   - Simple migration: if db doesn't exist, create it

9. SAMPLE DATA (scripts/seed_data.py):
   - Script to load 3-4 synthetic meeting notes for demo
   - Realistic content:
     * Engineering standup notes
     * Client meeting summary
     * Sprint retrospective
     * Sales call notes

10. STARTUP SCRIPTS:
    - run_backend.sh: Start FastAPI server on port 8000
    - run_frontend.sh: Start Streamlit on port 8501
    - setup.sh: Install dependencies, create database, seed data

STREAMLIT UI LAYOUT:

┌─────────────────────────────────────────┐
│         Virtual Representatives          │
├──────────────┬──────────────────────────┤
│  Sidebar:    │  Main Area:              │
│              │                           │
│  ○ Engineering│  💬 Chat History        │
│  ○ Delivery  │  (Engineering Rep)       │
│  ○ Admin     │                          │
│  ○ Sales     │  User: What's the status?│
│  ○ C-level   │  Bot: [response]         │
│  ○ Marketing │                          │
│              │  ──────────────────────  │
│  [Upload]    │  [Chat input box]        │
│  Documents   │                          │
└──────────────┴──────────────────────────┘
ADDITIONAL REQUIREMENTS:
- Add helpful comments explaining key functions
- Include error handling and user-friendly error messages
- Add logging for debugging
- Create README.md with:
  * Setup instructions
  * How to run (backend + frontend)
  * How to use Ollama
  * Example usage
- Make it hackathon-ready: prioritize working code over perfection

IMPORTANT DETAILS:
- Backend runs on http://localhost:8000
- Frontend runs on http://localhost:8501
- Frontend makes HTTP requests to backend
- Use st.session_state to maintain conversation history
- Show spinner/loading indicator during LLM calls
- Allow users to switch departments and see different "personalities"

START BY:
1. Creating the project structure
2. Setting up SQLite database with SQLAlchemy
3. Implementing the FastAPI backend with upload + chat endpoints
4. Creating basic Streamlit UI with department selector
5. Testing with one department (Engineering)

