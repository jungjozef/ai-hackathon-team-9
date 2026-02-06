#!/usr/bin/env bash
# Start the React (Lovable) frontend on port 5173
set -e
cd "$(dirname "$0")"
streamlit run frontend/app.py --server.port 8501
