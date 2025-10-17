@echo off
echo ========================================
echo 🛋️ Starting FurniCraft E-Commerce Platform
echo ========================================

echo.
echo 📁 Project Structure:
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo.

echo 🚀 Starting Backend Server...
start cmd /k "cd /d D:\aarushii-project\backend && echo Backend starting... && python main.py"

echo.
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo 🎨 Starting Frontend Server...
start cmd /k "cd /d D:\aarushii-project\frontend && echo Frontend starting... && npm start"

echo.
echo ✅ Both servers are starting!
echo.
echo 💡 How to use:
echo   1. Wait for both servers to fully start
echo   2. Backend will be at http://localhost:8000
echo   3. Frontend will be at http://localhost:3000
echo   4. API documentation at http://localhost:8000/docs
echo.
echo 🛑 To stop servers: Close both command windows or press Ctrl+C
echo.

pause