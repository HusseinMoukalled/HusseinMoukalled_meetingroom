@echo off
REM Script to start all services locally on Windows (without Docker)

echo Starting Smart Meeting Room Management System Services...

REM Start Users Service
echo Starting Users Service on port 8001...
start "Users Service" cmd /k "cd users_service && uvicorn app.main:app --port 8001 --reload"

REM Start Rooms Service
echo Starting Rooms Service on port 8002...
start "Rooms Service" cmd /k "cd rooms_service && uvicorn app.main:app --port 8002 --reload"

REM Start Bookings Service
echo Starting Bookings Service on port 8003...
start "Bookings Service" cmd /k "cd bookings_service && uvicorn app.main:app --port 8003 --reload"

REM Start Reviews Service
echo Starting Reviews Service on port 8004...
start "Reviews Service" cmd /k "cd reviews_service && uvicorn app.main:app --port 8004 --reload"

echo.
echo All services started!
echo Users Service: http://localhost:8001
echo Rooms Service: http://localhost:8002
echo Bookings Service: http://localhost:8003
echo Reviews Service: http://localhost:8004
echo.
echo Close the service windows to stop them.

pause

