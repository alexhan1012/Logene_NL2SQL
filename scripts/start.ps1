# Start both backend and frontend servers
Write-Host "🚀 Starting Logene NL2SQL services..." -ForegroundColor Cyan

# Start backend
Write-Host "`n📱 Starting backend on http://localhost:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList `
  "cd $PSScriptRoot\..; uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000" `
  -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 2

# Start frontend
Write-Host "🎨 Starting frontend on http://localhost:5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList `
  "cd $PSScriptRoot\..\frontend; npm run dev" `
  -WindowStyle Normal

Write-Host "`n✅ Services started!" -ForegroundColor Green
Write-Host "`n📍 Access the application:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "`n💡 Close the opened windows or press Ctrl+C to stop services" -ForegroundColor Cyan
