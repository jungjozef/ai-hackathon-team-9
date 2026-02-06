# Virtual Department Representatives

An AI-powered system that lets you chat with virtual representatives from different departments (Engineering, Delivery, Admin, Sales, C-level, Marketing). Each representative has a unique persona and answers questions based on your uploaded knowledge base.

Built with **FastAPI**, **Streamlit**, **SQLAlchemy**, and **Ollama** for local LLM inference.

## Quick Start

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai) installed and running

### 1. Pull an LLM model

```bash
ollama pull llama3.2
```

### 2. Run setup

```bash
chmod +x setup.sh run_backend.sh run_frontend.sh
./setup.sh
```

This installs dependencies, creates the SQLite database, and seeds it with sample meeting notes.

### 3. Start the backend (Terminal 1)

```bash
./run_backend.sh
```

The API will be available at http://localhost:8000. You can explore the docs at http://localhost:8000/docs.

### 4. Start the frontend (Terminal 2)

```bash
./run_frontend.sh
```

Open http://localhost:8501 in your browser.

## Usage

1. **Select a department** from the sidebar (Engineering, Delivery, Admin, Sales, C-level, Marketing).
2. **Upload documents** (meeting notes, reports, etc.) using the sidebar file uploader.
3. **Ask questions** in the chat input. The representative will answer based on its persona and the uploaded knowledge base.
4. **Switch departments** to get different perspectives on the same information.

## Project Structure

```
├── backend/
│   ├── main.py               # FastAPI app & endpoints
│   ├── database.py            # SQLite/SQLAlchemy setup
│   ├── document_processor.py  # File parsing (txt, md, pdf)
│   └── llm.py                 # Ollama integration
├── frontend/
│   └── app.py                 # Streamlit UI
├── shared/
│   ├── models.py              # SQLAlchemy models
│   └── personas.py            # Department persona definitions
├── scripts/
│   └── seed_data.py           # Sample data loader
├── data/                      # SQLite database (auto-created)
├── requirements.txt
├── setup.sh
├── run_backend.sh
└── run_frontend.sh
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/departments` | List all departments |
| GET | `/documents` | List uploaded documents |
| POST | `/upload/document` | Upload a document (multipart) |
| POST | `/chat` | Chat with a department rep |
| DELETE | `/documents/{id}` | Delete a document |

## Troubleshooting

- **"Cannot reach the backend API"** – Make sure the FastAPI server is running (`./run_backend.sh`).
- **"Cannot connect to Ollama"** – Run `ollama serve` in a terminal, then `ollama pull llama3.2`.
- **Slow responses** – Local LLM inference depends on your hardware. Try a smaller model like `mistral` if `llama3.2` is too slow.
