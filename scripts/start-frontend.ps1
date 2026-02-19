# Start frontend server only
Write-Host "🎨 Starting frontend server..." -ForegroundColor Cyan
Write-Host "UI: http://localhost:5173" -ForegroundColor Green
Write-Host "`nPress Ctrl+C to stop`n" -ForegroundColor Yellow

cd $PSScriptRoot\..\frontend
npm run dev
