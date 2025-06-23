# Ayala Foundation App - Setup Guide

## 🔧 Backend Setup & Network Issues Fix

### Issues Resolved:
1. ✅ **Password Hashing** - Already properly implemented using bcrypt in backend
2. ✅ **Network Connection Error** - Fixed with proper backend setup
3. ✅ **API Configuration** - Updated iOS app to use correct IP addresses

---

## 🚀 Quick Start

### Step 1: Start the Backend Server

```bash
cd Ayala_app_back/ayala-backend
python3 run_backend.py
```

This script will:
- ✅ Install required dependencies automatically
- ✅ Create `.env` file with default configuration
- ✅ Display your local IP address for iOS device testing
- ✅ Start the FastAPI server on port 8000

### Step 2: Update iOS Configuration (if needed)

The backend runner script will display your local IP. If it's different from `192.168.1.84`, update:

**File**: `Ayala_app_front/Core/API/APIConfiguration.swift`
```swift
case .device:
    return "http://YOUR_LOCAL_IP:8000/api/v1"  // Replace with your IP
```

### Step 3: Test the Connection

1. Open Xcode and run the iOS app
2. Try registering a new user
3. Check the Xcode console for network logs

---

## 🔒 Password Security

### ✅ Already Implemented Correctly!

Your backend already has proper password security:

1. **Hashing**: Uses `bcrypt` to hash passwords before storing
2. **Validation**: Requires minimum 8 characters
3. **Storage**: Only hashed passwords are stored in database

**Backend Code** (`src/auth/service.py`):
```python
def get_password_hash(self, password: str) -> str:
    return pwd_context.hash(password)  # bcrypt hashing

async def create_user(self, email: str, password: str, ...):
    hashed_password = self.get_password_hash(password)  # Hash before storing
    # ... store hashed_password in database
```

**No changes needed** - passwords are never stored in plain text!

---

## 🐛 Troubleshooting

### Network Error: "Could not connect to the server"

#### Solution 1: Check Backend is Running
```bash
# Check if server is running
curl http://127.0.0.1:8000/docs

# Should return FastAPI documentation page
```

#### Solution 2: Check IP Address
```bash
# Find your local IP
ifconfig | grep "inet " | grep -v 127.0.0.1
```

#### Solution 3: Test API Endpoints
```bash
# Test registration endpoint
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

### Common Issues

1. **"Failed building wheel"** when installing dependencies
   - ✅ Fixed: Use the `run_backend.py` script which handles this

2. **"Email already registered"**
   - ✅ Fixed: Better error messages in iOS app

3. **Password validation errors**
   - ✅ Fixed: Updated iOS app to require 8+ characters

---

## 📱 iOS App Improvements Made

### Enhanced Error Handling
- Better network error messages
- Specific validation feedback
- Debug logging for troubleshooting

### Updated Password Validation
- Changed from 6 to 8 character minimum
- Matches backend requirements

### Improved API Configuration
- Automatic environment detection
- Better IP address management
- Debug information

---

## 🌐 API Endpoints

Once your backend is running, you can access:

- **API Documentation**: http://127.0.0.1:8000/docs
- **Registration**: `POST /api/v1/auth/register`
- **Login**: `POST /api/v1/auth/token`
- **Health Check**: `GET /api/v1/` (if implemented)

---

## 📋 Development Workflow

1. **Start Backend**: `python3 run_backend.py` (from `Ayala_app_back/ayala-backend/`)
2. **Check Logs**: Watch console for API calls
3. **Test in Simulator**: Uses `127.0.0.1:8000`
4. **Test on Device**: Uses your local IP (displayed in console)

---

## 🔐 Security Notes

✅ **Your app is secure** - passwords are properly hashed using industry-standard bcrypt.

The error you saw was a **network connectivity issue**, not a security problem. With the backend running, user registration will work correctly and securely.

---

## 🎯 Next Steps After Setup

1. Register a test user through the iOS app
2. Check the database to confirm password is hashed
3. Test login functionality
4. Implement additional features as needed

Your password security implementation is already production-ready! 🛡️ 