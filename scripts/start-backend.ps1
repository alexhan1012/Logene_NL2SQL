# Start backend server only
Write-Host "📱 Starting backend server..." -ForegroundColor Cyan
Write-Host "API: http://localhost:8000" -ForegroundColor Green
Write-Host "Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "`nPress Ctrl+C to stop`n" -ForegroundColor Yellow

cd $PSScriptRoot\..
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
