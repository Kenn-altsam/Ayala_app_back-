# Ayala Foundation - Project Structure

## 📁 Directory Organization

```
Ayala_app_back/
├── ayala-backend/          # 🚀 Main Backend Application
│   ├── src/                # Source code
│   │   ├── auth/           # Authentication logic
│   │   ├── companies/      # Company management
│   │   ├── funds/          # Fund management
│   │   ├── core/           # Core utilities
│   │   └── main.py         # FastAPI application entry point
│   ├── migrations/         # Database migrations
│   ├── requirements.txt    # Python dependencies
│   ├── alembic.ini        # Database migration config
│   ├── run_backend.py     # Local development server
│   ├── deploy_to_server.sh # Deployment script
│   ├── SETUP_GUIDE.md     # Local setup instructions
│   └── REMOTE_SERVER_GUIDE.md # Remote deployment guide
├── docker-compose.yml      # Docker configuration
├── nginx.conf             # Nginx configuration
├── start_backend.sh       # Alternative startup script
└── README.md              # Main project documentation
```

---

## 🔄 What Changed

### ✅ Renamed Directory
- **Old**: `Ayala_app_back/+/` ❌ (unprofessional)
- **New**: `Ayala_app_back/ayala-backend/` ✅ (clear and descriptive)

### ✅ Benefits of New Structure
1. **Professional naming** - No more confusing `+` symbols
2. **Clear purpose** - `ayala-backend` clearly indicates this is the backend code
3. **Better organization** - Follows standard project naming conventions
4. **Easier navigation** - Developers can quickly understand the structure

---

## 🚀 Quick Commands

### Local Development
```bash
# Start local backend server
cd Ayala_app_back/ayala-backend
python3 run_backend.py
```

### Remote Deployment
```bash
# Deploy to production server
cd Ayala_app_back/ayala-backend
./deploy_to_server.sh
```

### Docker Deployment
```bash
# Use Docker (from parent directory)
cd Ayala_app_back
docker-compose up -d
```

---

## 📱 iOS App Configuration

The iOS app automatically connects to:
- **Local Development**: `http://127.0.0.1:8000/api/v1` (Simulator)
- **Local Network**: `http://192.168.1.84:8000/api/v1` (Device)
- **Remote Server**: `http://142.93.103.143:8000/api/v1` (Production)

Current configuration points to the remote server for both simulator and device.

---

## 🔧 File Locations

### Backend Code
- **Main App**: `ayala-backend/src/main.py`
- **Authentication**: `ayala-backend/src/auth/`
- **API Routes**: `ayala-backend/src/*/router.py`
- **Database Models**: `ayala-backend/src/*/models.py`

### Configuration
- **Environment**: `ayala-backend/.env`
- **Dependencies**: `ayala-backend/requirements.txt`
- **Database**: `ayala-backend/alembic.ini`

### Deployment
- **Local**: `ayala-backend/run_backend.py`
- **Remote**: `ayala-backend/deploy_to_server.sh`
- **Docker**: `docker-compose.yml`

---

## 🎯 Next Steps

1. ✅ Directory renamed to `ayala-backend`
2. ✅ All documentation updated
3. ✅ iOS app configured for remote server
4. 🔄 Ready for deployment to `142.93.103.143`

The project now has a much cleaner and more professional structure! 🌟 