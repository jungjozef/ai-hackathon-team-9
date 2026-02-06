#!/usr/bin/env bash
# Start the Lovable React frontend on port 5173
set -e
cd "$(dirname "$0")"
FRONTEND_DIR="lovable-frontend"
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
  npm install
fi

npm run dev -- --host 0.0.0.0 --port 5173
