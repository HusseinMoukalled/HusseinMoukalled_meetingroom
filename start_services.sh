#!/bin/bash

# Script to start all services locally (without Docker)

echo "Starting Smart Meeting Room Management System Services..."

# Start Users Service
echo "Starting Users Service on port 8001..."
cd users_service
uvicorn app.main:app --port 8001 --reload &
USERS_PID=$!
cd ..

# Start Rooms Service
echo "Starting Rooms Service on port 8002..."
cd rooms_service
uvicorn app.main:app --port 8002 --reload &
ROOMS_PID=$!
cd ..

# Start Bookings Service
echo "Starting Bookings Service on port 8003..."
cd bookings_service
uvicorn app.main:app --port 8003 --reload &
BOOKINGS_PID=$!
cd ..

# Start Reviews Service
echo "Starting Reviews Service on port 8004..."
cd reviews_service
uvicorn app.main:app --port 8004 --reload &
REVIEWS_PID=$!
cd ..

echo "All services started!"
echo "Users Service: http://localhost:8001"
echo "Rooms Service: http://localhost:8002"
echo "Bookings Service: http://localhost:8003"
echo "Reviews Service: http://localhost:8004"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "kill $USERS_PID $ROOMS_PID $BOOKINGS_PID $REVIEWS_PID; exit" INT TERM
wait

