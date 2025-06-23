#!/bin/bash

# Ayala Foundation Backend Setup Script

set -e

echo "🚀 Setting up Ayala Foundation Backend..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p back/logs
mkdir -p data/postgres
mkdir -p data/redis

# Create environment file if it doesn't exist
if [ ! -f back/.env ]; then
    echo "📄 Creating .env file..."
    cat > back/.env << EOF
# Database Configuration
POSTGRES_SERVER=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_DB=ayala_foundation
POSTGRES_PORT=5432

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Security (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production

# OpenAI Configuration (optional)
OPENAI_API_KEY=your-openai-api-key-here

# Application Settings
PROJECT_NAME=Ayala Foundation API
VERSION=1.0.0
API_V1_STR=/api/v1
EOF
    echo "⚠️  Please update the passwords and secret keys in back/.env file for production!"
fi

# Build and start services
echo "🐳 Building Docker containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 15

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec -T api alembic upgrade head

echo "✅ Setup complete!"
echo ""
echo "🌐 Services running:"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Health Check: http://localhost:8000/api/v1/health"
echo ""
echo "🔧 Useful commands:"
echo "  docker-compose logs -f          # View logs"
echo "  docker-compose ps               # Check status"
echo "  docker-compose down             # Stop services"
echo "  docker-compose restart api      # Restart API" 