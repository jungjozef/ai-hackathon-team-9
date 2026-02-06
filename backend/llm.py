"""Ollama LLM integration – builds prompts with persona context and queries the model."""

import logging
import os

import ollama
from sqlalchemy.orm import Session

from shared.models import Document
from shared.personas import get_dashboard_prompt, get_persona

logger = logging.getLogger(__name__)

MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
FALLBACK_MODEL = os.getenv("OLLAMA_FALLBACK_MODEL", "llama3.1:8b")


def _fetch_context(db: Session, limit: int = 10) -> str:
    """Fetch the most recent documents and format them as context for the LLM."""
    docs = db.query(Document).order_by(Document.upload_date.desc()).limit(limit).all()
    if not docs:
        return "No documents available in the knowledge base yet."

    parts = []
    for doc in docs:
        parts.append(f"--- {doc.title} (uploaded {doc.upload_date}) ---\n{doc.content}")
    return "\n\n".join(parts)


def chat(
    department: str, user_message: str, db: Session, history: list[dict] | None = None
) -> str:
    """
    Send a chat request to Ollama using the specified department persona.

    Returns the assistant's reply text.
    Raises RuntimeError if Ollama is unreachable.
    """
    persona = get_persona(department)
    if persona is None:
        return f"Unknown department: {department}"

    context = _fetch_context(db)

    system_message = (
        f"{persona['system_prompt']}\n\n"
        "Below is the current knowledge base. Use it to ground your answers:\n\n"
        f"{context}"
    )

    # Build the messages list for the Ollama API
    messages = [{"role": "system", "content": system_message}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    # Try primary model, then fallback
    last_error = None
    for model in (MODEL, FALLBACK_MODEL):
        try:
            logger.info("Querying Ollama model=%s department=%s", model, department)
            logger.info("Sending %d messages to Ollama", len(messages))
            response = ollama.chat(model=model, messages=messages)
            logger.info("Ollama response type: %s", type(response))
            logger.info("Ollama response keys: %s", response.keys() if hasattr(response, 'keys') else dir(response))

            # Handle both dict-style and attribute-style access (depends on ollama library version)
            if hasattr(response, "message"):
                msg = response.message
                content = msg.content if hasattr(msg, "content") else msg.get("content", "")
            elif isinstance(response, dict) and "message" in response:
                content = response["message"]["content"]
            else:
                logger.error("Unexpected response format: %s", response)
                content = str(response)

            logger.info("Got reply from Ollama (%d chars)", len(content))
            return content
        except ollama.ResponseError as e:
            logger.warning("Model %s ResponseError: %s", model, e)
            last_error = e
            continue
        except Exception as e:
            logger.error("Model %s unexpected error (%s): %s", model, type(e).__name__, e)
            last_error = e
            continue

    error_detail = f" Last error: {type(last_error).__name__}: {last_error}" if last_error else ""
    logger.error("All models failed. Tried: %s, %s.%s", MODEL, FALLBACK_MODEL, error_detail)
    return (
        f"Sorry, no LLM model is available. Tried models: {MODEL}, {FALLBACK_MODEL}. "
        f"Make sure Ollama is running and has a model pulled.{error_detail}"
    )


def generate_dashboard(department: str, db: Session) -> str:
    """Generate a department dashboard by feeding all documents into the department-specific dashboard prompt.

    Returns Markdown content. Raises RuntimeError if all models fail.
    """
    dashboard_prompt = get_dashboard_prompt(department)
    if dashboard_prompt is None:
        raise ValueError(f"No dashboard prompt defined for department: {department}")

    context = _fetch_context(db, limit=50)  # pull more docs for the dashboard

    system_message = (
        f"{dashboard_prompt}\n\n"
        "=== KNOWLEDGE BASE DOCUMENTS ===\n\n"
        f"{context}"
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": "Generate the dashboard now based on all available documents."},
    ]

    last_error = None
    for model in (MODEL, FALLBACK_MODEL):
        try:
            logger.info("Generating dashboard model=%s department=%s", model, department)
            response = ollama.chat(model=model, messages=messages)

            if hasattr(response, "message"):
                msg = response.message
                content = msg.content if hasattr(msg, "content") else msg.get("content", "")
            elif isinstance(response, dict) and "message" in response:
                content = response["message"]["content"]
            else:
                content = str(response)

            logger.info("Dashboard generated for %s (%d chars)", department, len(content))
            return content
        except ollama.ResponseError as e:
            logger.warning("Dashboard model %s ResponseError: %s", model, e)
            last_error = e
            continue
        except Exception as e:
            logger.error("Dashboard model %s error (%s): %s", model, type(e).__name__, e)
            last_error = e
            continue

    raise RuntimeError(
        f"Failed to generate dashboard. Tried: {MODEL}, {FALLBACK_MODEL}. "
        f"Last error: {last_error}"
    )
