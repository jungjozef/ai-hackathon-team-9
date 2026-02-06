#!/usr/bin/env bash
# Start the React (Lovable) frontend on port 5173
set -e
cd "$(dirname "$0")/lovable-frontend"

if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm install
fi

npm run dev -- --host 0.0.0.0 --port 5173
