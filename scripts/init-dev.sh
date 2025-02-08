#!/bin/bash

# Exit on error
set -e

echo "Setting up development environment..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

# Build and start containers
echo "Starting Docker containers..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 5

# Run database migrations
echo "Running database migrations..."
docker-compose -f docker-compose.dev.yml exec app alembic upgrade head

# Create initial test data
echo "Creating initial test data..."
docker-compose -f docker-compose.dev.yml exec app python scripts/create_test_data.py

echo "Development environment is ready!"
echo "API is running at http://localhost:8000"
echo "API docs are available at http://localhost:8000/api/docs"
echo "PgAdmin is available at http://localhost:5050" 