#!/usr/bin/env bash
# One-time setup: install dependencies, create database, seed sample data
set -e
cd "$(dirname "$0")"

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo ""
echo "=== Initializing database and seeding sample data ==="
python scripts/seed_data.py

echo ""
echo "=== Setup complete! ==="
echo ""
echo "To start the system:"
echo "  Terminal 1:  ./run_backend.sh"
echo "  Terminal 2:  ./run_frontend.sh"
echo ""
echo "Make sure Ollama is running:  ollama serve"
echo "And that you have a model:    ollama pull llama3.2"
