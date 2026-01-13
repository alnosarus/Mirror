#!/bin/bash

# Mirror Project - Startup Script
# This script starts both the API server and frontend development server

echo "🚀 Starting Mirror Project..."
echo ""

# Check if PostgreSQL is running
if ! pgrep -x postgres > /dev/null; then
    echo "❌ PostgreSQL is not running!"
    echo "Start it with: brew services start postgresql@17"
    exit 1
fi

echo "✓ PostgreSQL is running"

# Check for .env file and load it
if [ -f .env ]; then
    echo "✓ Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  No .env file found - AI agent will not work without ANTHROPIC_API_KEY"
    echo "   Create .env from .env.example and add your API key"
fi

# Start API server in background
echo "📡 Starting API server on http://localhost:5001..."
python3 api_server.py > logs/api.log 2>&1 &
API_PID=$!
sleep 2

# Check if API server started successfully
if ! curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
    echo "❌ API server failed to start"
    echo "Check logs/api.log for errors"
    exit 1
fi

echo "✓ API server running (PID: $API_PID)"

# Start frontend dev server
echo "🎨 Starting frontend on http://localhost:5174..."
cd app
npm run dev

# When frontend is stopped (Ctrl+C), also stop API server
echo ""
echo "🛑 Stopping servers..."
kill $API_PID 2>/dev/null
echo "✓ All servers stopped"
