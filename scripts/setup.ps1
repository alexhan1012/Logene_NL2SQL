# Setup script for the project
# Run this first to install all dependencies

Write-Host "🚀 Setting up Logene NL2SQL project..." -ForegroundColor Cyan

# Check if uv is installed
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "❌ uv is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "   iwr https://astral.sh/uv/install.ps1 | iex"
    exit 1
}

# Check if nvm is installed
if (-not (Get-Command nvm -ErrorAction SilentlyContinue)) {
    Write-Host "❌ nvm is not installed. Please install it from:" -ForegroundColor Red
    Write-Host "   https://github.com/coreybutler/nvm-windows/releases"
    exit 1
}

Write-Host ✓ "uv and nvm found" -ForegroundColor Green

# Setup Python environment
Write-Host "`n📦 Installing Python dependencies with uv..." -ForegroundColor Cyan
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}

# Setup Node.js environment
Write-Host "`n📦 Installing Node.js v20 with nvm..." -ForegroundColor Cyan
nvm install 20
nvm use 20

# Setup frontend dependencies
Write-Host "`n📦 Installing frontend dependencies..." -ForegroundColor Cyan
Push-Location frontend
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "`n📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. Configure environment: cp backend\.env.example backend\.env"
Write-Host "2. Edit backend\.env with your API keys"
Write-Host "3. Start services: .\start.ps1"
Write-Host "`n💡 Or run individually:" -ForegroundColor Yellow
Write-Host "   .\start-backend.ps1  # Start backend on port 8000"
Write-Host "   .\start-frontend.ps1 # Start frontend on port 5173"
