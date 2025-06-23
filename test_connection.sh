#!/bin/bash

# Test Backend Connection Script
echo "🧪 Testing Ayala Foundation Backend Connection..."
echo ""

# Get local IP
LOCAL_IP=$(ifconfig | grep -E "inet.*broadcast" | grep -v "127.0.0.1" | awk '{print $2}' | head -1)

echo "🌐 Network Information:"
echo "   Local IP: $LOCAL_IP"
echo "   Localhost: 127.0.0.1"
echo ""

echo "📋 Testing Backend Endpoints..."
echo ""

# Test 1: Health Check (localhost)
echo "1️⃣ Testing health endpoint (localhost):"
curl -s http://localhost:8000/api/v1/health | jq '.' 2>/dev/null || curl -s http://localhost:8000/api/v1/health
echo ""

# Test 2: Health Check (local IP)
echo "2️⃣ Testing health endpoint (local IP for iOS device):"
curl -s http://$LOCAL_IP:8000/api/v1/health | jq '.' 2>/dev/null || curl -s http://$LOCAL_IP:8000/api/v1/health
echo ""

# Test 3: API Documentation
echo "3️⃣ Testing API documentation availability:"
if curl -s http://localhost:8000/docs | grep -q "FastAPI"; then
    echo "✅ API Documentation is accessible at http://localhost:8000/docs"
else
    echo "❌ API Documentation not accessible"
fi
echo ""

# Test 4: Registration endpoint (should return validation error)
echo "4️⃣ Testing registration endpoint:"
curl -s -X POST http://localhost:8000/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"short","full_name":"Test User"}' | \
    jq '.' 2>/dev/null || echo "Endpoint responding but JSON parsing failed"
echo ""

echo "📱 iOS App Configuration:"
echo "   Simulator URL: http://127.0.0.1:8000/api/v1"
echo "   Device URL: http://$LOCAL_IP:8000/api/v1"
echo ""

echo "✅ Backend connection tests completed!"
echo "   If all tests show responses, your backend is working correctly."
echo "   Your iOS app should now be able to connect to the backend." 