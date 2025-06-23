#!/bin/bash

# Start Backend Script for Ayala Foundation
# This script starts the backend and shows the IP address for frontend configuration

echo "🚀 Starting Ayala Foundation Backend..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Get local IP address
echo "🌐 Network Configuration:"
echo "   Getting your local IP address..."

# For macOS/Linux
LOCAL_IP=$(ifconfig | grep -E "inet.*broadcast" | grep -v "127.0.0.1" | awk '{print $2}' | head -1)

if [ -z "$LOCAL_IP" ]; then
    # Alternative method for different systems
    LOCAL_IP=$(hostname -I | awk '{print $1}')
fi

if [ -z "$LOCAL_IP" ]; then
    echo "   ⚠️  Could not automatically detect IP address"
    echo "   📝 Please run: ifconfig | grep inet"
    echo "   🔍 Look for your local IP (usually 192.168.x.x or 10.0.x.x)"
else
    echo "   ✅ Local IP Address: $LOCAL_IP"
fi

echo ""
echo "📱 Frontend Configuration:"
echo "   In your iOS app, update APIConfiguration.swift:"
echo "   Change the device URL to: http://$LOCAL_IP:8000/api/v1"
echo ""

# Start the backend services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 5

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Backend services are running!"
    echo ""
    echo "🌐 API Endpoints:"
    echo "   • Health Check: http://localhost:8000/api/v1/health"
    echo "   • API Documentation: http://localhost:8000/docs"
    echo "   • For iOS Simulator: http://127.0.0.1:8000/api/v1"
    echo "   • For iOS Device: http://$LOCAL_IP:8000/api/v1"
    echo ""
    echo "📊 Database:"
    echo "   • PostgreSQL: localhost:5432"
    echo "   • Redis: localhost:6379"
    echo ""
    echo "🔍 To view logs: docker-compose logs -f"
    echo "🛑 To stop: docker-compose down"
else
    echo ""
    echo "❌ Some services failed to start. Check the logs:"
    echo "   docker-compose logs"
fi

echo ""
echo "🎯 Next Steps:"
echo "   1. Update your iOS app's APIConfiguration.swift with the correct IP"
echo "   2. Test the connection with: curl http://localhost:8000/api/v1/health"
echo "   3. Run your iOS app and test the API connection"
echo "" 