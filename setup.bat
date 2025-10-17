@echo off
echo 🛋️ Setting up Furniture Website using AI and ML
echo.

echo 📦 Installing Backend Dependencies...
cd backend
pip install fastapi uvicorn pandas numpy sentence-transformers scikit-learn python-multipart
echo.

echo 📦 Installing Frontend Dependencies...
cd ..\frontend
npm install
npm install chart.js react-chartjs-2
echo.

echo ✅ Setup Complete!
echo.
echo 🚀 To start the application:
echo   1. Backend: cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
echo   2. Frontend: cd frontend && npm start
echo.
echo 🌐 Access the application at:
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://127.0.0.1:8000
echo   - Analytics: http://localhost:3000/analytics
echo.
pause