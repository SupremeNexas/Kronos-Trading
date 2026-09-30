#!/usr/bin/env bash
echo "Starting Kronos Backend..."
export PORT=7070
export FLASK_ENV=development
export MARKET_DATA_PROVIDER=mock
export TRADING_MODE=paper

# Run python in background
.venv/bin/python wsgi.py &
BACKEND_PID=$!

echo "Starting Kronos Frontend..."
cd frontend
export NEXT_PUBLIC_API_URL=http://localhost:7070
npm run dev &
FRONTEND_PID=$!

echo "Kronos is running!"
echo "Backend: http://localhost:7070"
echo "Frontend: http://localhost:3000"

# Kill both on Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM
wait
