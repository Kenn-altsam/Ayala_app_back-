# Backend-Frontend Connection Guide

This guide will help you connect your Ayala_app_back (FastAPI backend) with your Ayala_app_front (iOS Swift frontend).

## 🚀 Quick Setup

### Step 1: Start the Backend

1. Open Terminal and navigate to the backend directory:
```bash
cd /Users/kenn_/nfac/Ayala_app_back
```

2. Run the startup script:
```bash
./start_backend.sh
```

This script will:
- Start all Docker services (PostgreSQL, Redis, FastAPI)
- Show your local IP address
- Display all important URLs

### Step 2: Configure Frontend for Your Network

The iOS app automatically detects whether it's running on simulator or device:

**For iOS Simulator**: Uses `http://127.0.0.1:8000/api/v1` (localhost)
**For iOS Device**: Uses `http://192.168.1.100:8000/api/v1` (your computer's IP)

⚠️ **Important**: Update the IP address in `APIConfiguration.swift`:

1. From the startup script output, copy your actual IP address
2. Edit `Ayala_app/Ayala_app_front/Ayala_app_front/Core/API/APIConfiguration.swift`
3. Replace `192.168.1.100` with your actual IP address

### Step 3: Test the Connection

1. Run your iOS app in Xcode
2. The app will automatically print the current configuration in the debug console
3. Use the "Test Backend Connection" button to verify connectivity

## 🔧 Manual Configuration

If you need to manually set the backend URL, edit `APIConfiguration.swift`:

```swift
// Uncomment and set this to override automatic detection
static let baseURL = "http://YOUR_COMPUTER_IP:8000/api/v1"
```

## 🌐 API Endpoints Available

Your backend provides these endpoints:

### Authentication
- `POST /api/v1/auth/token` - Login with email/password
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/google/verify` - Google OAuth login
- `POST /api/v1/auth/password-reset-request` - Request password reset

### Companies
- `GET /api/v1/companies/search` - Search companies
- `GET /api/v1/companies/ai-search` - AI-powered search
- `GET /api/v1/companies/ai-suggestions` - Get AI suggestions
- `GET /api/v1/companies/{id}` - Get company details

### Funds
- `GET/POST /api/v1/funds/profile` - Manage fund profile
- `POST /api/v1/funds/conversation` - AI conversation

### Health Check
- `GET /api/v1/health` - Service health status

## 🛠️ Troubleshooting

### Backend Issues

1. **Docker not running**:
```bash
# Start Docker Desktop, then run:
docker-compose up -d
```

2. **Port 8000 already in use**:
```bash
# Find and kill the process using port 8000:
lsof -ti:8000 | xargs kill -9
```

3. **Database connection issues**:
```bash
# Reset the database:
docker-compose down -v
docker-compose up -d
```

### Frontend Issues

1. **Connection failed on device**:
   - Ensure your iPhone/iPad is on the same WiFi network as your computer
   - Update the IP address in `APIConfiguration.swift`
   - Disable firewall or allow port 8000

2. **Connection failed on simulator**:
   - Backend should be running on `localhost:8000`
   - Check if port 8000 is accessible: `curl http://localhost:8000/api/v1/health`

3. **Build errors in Xcode**:
   - Clean build folder: Product → Clean Build Folder
   - Reset package cache: File → Packages → Reset Package Caches

## 📱 Network Configuration

### Find Your IP Address

**Method 1**: Use the startup script (automatically shows IP)
```bash
./start_backend.sh
```

**Method 2**: Manual command
```bash
ifconfig | grep -E "inet.*broadcast" | grep -v "127.0.0.1" | awk '{print $2}'
```

**Method 3**: System Preferences
- System Preferences → Network → WiFi → Advanced → TCP/IP

### Common IP Ranges
- **Home networks**: `192.168.1.x` or `192.168.0.x`
- **Office networks**: `10.0.0.x` or `172.16.x.x`

## 🔐 CORS Configuration

The backend is configured to allow all origins (`*`) for development. For production, update `ALLOWED_ORIGINS` in `src/core/config.py`.

## 📊 Monitoring

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres
```

### Check Service Status
```bash
docker-compose ps
```

### Stop Services
```bash
docker-compose down
```

## 🚀 Production Deployment

For production deployment:

1. Update `APIConfiguration.swift` with your production domain:
```swift
static let baseURL = "https://your-domain.com/api/v1"
```

2. Configure proper CORS settings in the backend
3. Use HTTPS certificates
4. Set up proper environment variables

## 📝 Next Steps

1. Start the backend: `./start_backend.sh`
2. Update frontend IP configuration
3. Test connection in your iOS app
4. Start developing your app features!

## 🆘 Need Help?

If you encounter any issues:
1. Check the logs: `docker-compose logs -f`
2. Test the health endpoint: `curl http://localhost:8000/api/v1/health`
3. Verify your network configuration
4. Ensure Docker is running and has sufficient resources 