#!/bin/bash

# PORTNET® AI Incident Management System Startup Script
# This script starts both the backend API and frontend Streamlit app

echo "=========================================="
echo "PORTNET® AI Incident Management System"
echo "Starting Backend and Frontend..."
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if in portnet directory
if [ ! -f "portnet.db" ]; then
    echo "⚠️  Warning: Database file not found. Make sure you're in the portnet directory."
fi

# Start Backend API in background
echo "🚀 Starting Backend FastAPI Server..."
cd backend/api
python3 -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID) on http://localhost:8000"
echo ""

# Wait for backend to be ready
echo "⏳ Waiting for backend to initialize..."
sleep 3
echo ""

# Start Frontend Streamlit
echo "🚀 Starting Frontend Streamlit App..."
cd ../../
streamlit run frontend/Dashboard.py --server.port 8501 --server.address localhost &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID) on http://localhost:8501"
echo ""

echo "=========================================="
echo "✅ System is now running!"
echo "=========================================="
echo ""
echo "📊 Frontend Dashboard: http://localhost:8501"
echo "🔧 Backend API Docs:   http://localhost:8000/docs"
echo "❤️  Backend Health:     http://localhost:8000/api/health"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo 'Shutting down...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT

# Keep script running
wait

