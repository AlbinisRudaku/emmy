Write-Host "Setting up development environment..."

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file..."
    Copy-Item .env.example .env
}

# Build and start containers
Write-Host "Starting Docker containers..."
docker compose -f docker-compose.dev.yml up -d

# Wait for database to be ready
Write-Host "Waiting for database to be ready..."
Start-Sleep -Seconds 5

# Run database migrations
Write-Host "Running database migrations..."
docker compose -f docker-compose.dev.yml exec app alembic upgrade head

# Create initial test data
Write-Host "Creating initial test data..."
docker compose -f docker-compose.dev.yml exec app python scripts/create_test_data.py

Write-Host "Development environment is ready!"
Write-Host "API is running at http://localhost:8000"
Write-Host "API docs are available at http://localhost:8000/api/docs"
Write-Host "PgAdmin is available at http://localhost:5050"

# Keep the window open
Write-Host "Press any key to close..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown') 