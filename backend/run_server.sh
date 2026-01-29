#!/bin/bash
# Provolution Gamification API - Unix Run Script
# Usage: ./run_server.sh [port]

PORT=${1:-8000}

echo ""
echo "========================================"
echo " Provolution Gamification API"
echo " Starting on http://localhost:$PORT"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "No virtual environment found. Using system Python."
    echo "Tip: Create venv with: python -m venv venv"
fi

echo ""
echo "Starting server..."
echo "Docs available at: http://localhost:$PORT/docs"
echo ""

uvicorn app.main:app --reload --port $PORT
