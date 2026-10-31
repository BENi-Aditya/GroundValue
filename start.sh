#!/bin/bash
# Start GroundValue with new React frontend

echo "🚀 Starting GroundValue..."
echo ""

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing Flask..."
    pip3 install flask flask-cors
    echo ""
fi

# Start Flask API
echo "🔧 Starting Flask API on port 5000..."
cd groundvalue_mvp
python3 api.py &
API_PID=$!
cd ..

# Wait for API to start
sleep 3

# Start React frontend
echo "⚛️  Starting React frontend on port 3000..."
python3 -m http.server 3000 --directory frontend &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 2

echo ""
echo "✅ GroundValue is running!"
echo ""
echo "📱 Access your application:"
echo "   • New React UI:     http://localhost:3000"
echo "   • Original App:     http://localhost:8501/?view=app"
echo "   • Landing Page:     http://localhost:8501"
echo ""
echo "📋 Process IDs:"
echo "   • API: $API_PID"
echo "   • Frontend: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Trap Ctrl+C to kill all processes
trap "kill $API_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Keep script running
wait
