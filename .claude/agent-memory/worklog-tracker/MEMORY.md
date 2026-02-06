# Worklog Tracker Memory

## Project Overview
- **Project:** Virtual Department Representatives (Hackathon)
- **Tech Stack:** FastAPI + Streamlit + Ollama + SQLite
- **Status:** Currently implementing Google SSO authentication layer

## Key Components Implemented
1. Google OAuth 2.0 Integration (2026-02-06)
   - User authentication via Google
   - JWT-based session management
   - Protected API endpoints
   - Frontend login/logout flows

## Database Models
- Document: id, title, content, upload_date, tags, metadata
- User: id, email, name, google_id, created_at (NEW - for SSO)

## Department Personas
6 personas available: Engineering, Delivery, Admin, Sales, C-level, Marketing

## Important Architecture Notes
- Backend runs on :8000, Frontend on :8501
- CORS enabled for Streamlit
- Authentication: Google OAuth → JWT token → HTTP-only cookie
- Protected endpoints require valid token in request

## Files Modified
- shared/models.py: Added User model
- backend/auth.py: New OAuth implementation
- backend/main.py: Auth routes + endpoint protection
- frontend/app.py: Login screen + auth handling
- requirements.txt: Added auth libraries
- .env: OAuth config placeholders
