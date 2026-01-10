#!/bin/bash

# Mirror Project - Stop Script
# This script stops all running services

echo "🛑 Stopping Mirror Project..."

# Stop API server
if pgrep -f "api_server.py" > /dev/null; then
    pkill -f "api_server.py"
    echo "✓ API server stopped"
else
    echo "ℹ️  API server not running"
fi

# Stop Vite dev server
if pgrep -f "vite" > /dev/null; then
    pkill -f "vite"
    echo "✓ Frontend dev server stopped"
else
    echo "ℹ️  Frontend dev server not running"
fi

echo ""
echo "✅ All services stopped"
