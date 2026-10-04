#!/usr/bin/env bash
echo "Starting Kronos Trading Lab..."
export PORT=7070
export FLASK_ENV=development
export MARKET_DATA_PROVIDER=alpaca
export TRADING_MODE=paper

# Run backend
cd /Users/supryo/Desktop/Kronos-master
.venv/bin/python wsgi.py &
BACKEND_PID=$!

# Run automatic scheduler
.venv/bin/python webui/scheduler.py &
SCHEDULER_PID=$!

echo "Starting Kronos Frontend..."
cd frontend
export NEXT_PUBLIC_API_URL=http://localhost:7070
npm run dev &
FRONTEND_PID=$!

echo "Kronos Paper Trading Lab is running!"
echo "Backend: http://localhost:7070"
echo "Frontend: http://localhost:3000/paper-trading"

# Kill all on Ctrl+C
trap "kill $BACKEND_PID $SCHEDULER_PID $FRONTEND_PID; exit" SIGINT SIGTERM
wait
