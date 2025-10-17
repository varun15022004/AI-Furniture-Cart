#!/bin/bash

echo ""
echo "========================================"
echo "  FurniCraft E-commerce Platform"
echo "========================================"
echo ""

echo "Starting backend server..."
echo "Please wait for the backend to start completely."
echo ""

# Start backend in background
cd backend
gnome-terminal --title="FurniCraft Backend" -- bash -c "uvicorn main:app --reload; exec bash" &

# Wait for backend to start
echo "Waiting 10 seconds for backend to initialize..."
sleep 10

echo ""
echo "Starting frontend..."
cd ../frontend

# Install dependencies if not exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start frontend in new terminal
gnome-terminal --title="FurniCraft Frontend" -- bash -c "npm start; exec bash" &

echo ""
echo "========================================"
echo "  Both servers are starting!"
echo "========================================"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Enter to continue..."
read