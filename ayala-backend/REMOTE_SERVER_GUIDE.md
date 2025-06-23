# Ayala Foundation - Remote Server Deployment Guide

## 🌐 Server Information
- **Server IP**: `142.93.103.143`
- **Purpose**: Production/staging backend deployment
- **Port**: `8000` (for API)

---

## 🚀 Deployment Options

### Option 1: Automated Deployment (Recommended)

```bash
cd Ayala_app_back/ayala-backend
./deploy_to_server.sh
```

This script will:
- ✅ Copy your backend code to the server
- ✅ Install all dependencies
- ✅ Configure systemd service for auto-restart
- ✅ Open firewall port 8000
- ✅ Start the backend service

### Option 2: Manual Deployment

#### Step 1: Copy files to server
```bash
cd Ayala_app_back/ayala-backend
scp -r src/ root@142.93.103.143:/opt/ayala-backend/
scp requirements.txt root@142.93.103.143:/opt/ayala-backend/
```

#### Step 2: SSH into server and setup
```bash
ssh root@142.93.103.143

# Install dependencies
apt update && apt install -y python3 python3-pip python3-venv
cd /opt/ayala-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the server
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

---

## 🔧 Server Management Commands

### Check Service Status
```bash
ssh root@142.93.103.143 'systemctl status ayala-backend'
```

### View Live Logs
```bash
ssh root@142.93.103.143 'journalctl -u ayala-backend -f'
```

### Restart Service
```bash
ssh root@142.93.103.143 'systemctl restart ayala-backend'
```

### Stop Service
```bash
ssh root@142.93.103.143 'systemctl stop ayala-backend'
```

---

## 🧪 Testing Your Deployment

### 1. Test API Endpoints
```bash
# Health check
curl http://142.93.103.143:8000/docs

# Test registration
curl -X POST "http://142.93.103.143:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

### 2. Test from iOS App
Your iOS app is already configured to use `142.93.103.143:8000`. Simply:
1. Open Xcode
2. Run your app (Simulator or Device)
3. Try registering a new user
4. Check for successful connection

---

## 🛡️ Security Considerations

### Firewall Rules
```bash
# On your server
ufw allow 22      # SSH
ufw allow 8000    # API
ufw enable
```

### SSL/HTTPS Setup (Optional)
For production, consider setting up SSL:

1. **Install Nginx** (reverse proxy):
```bash
apt install nginx certbot python3-certbot-nginx
```

2. **Configure Nginx** (`/etc/nginx/sites-available/ayala`):
```nginx
server {
    listen 80;
    server_name 142.93.103.143;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Get SSL Certificate**:
```bash
certbot --nginx -d 142.93.103.143
```

---

## 🐛 Troubleshooting

### Issue: "Connection refused"
**Solution**: Check if service is running
```bash
ssh root@142.93.103.143 'systemctl status ayala-backend'
```

### Issue: "Port 8000 already in use"
**Solution**: Find and kill the process
```bash
ssh root@142.93.103.143 'lsof -i :8000'
ssh root@142.93.103.143 'kill -9 <PID>'
```

### Issue: iOS app can't connect
**Solutions**:
1. Check server firewall: `ufw status`
2. Verify service is running: `systemctl status ayala-backend`
3. Test with curl from your Mac: `curl http://142.93.103.143:8000/docs`

### Issue: Service won't start
**Solution**: Check logs
```bash
ssh root@142.93.103.143 'journalctl -u ayala-backend -n 50'
```

---

## 📊 Monitoring & Maintenance

### View Resource Usage
```bash
ssh root@142.93.103.143 'htop'
```

### Check Disk Space
```bash
ssh root@142.93.103.143 'df -h'
```

### Backup Database
```bash
ssh root@142.93.103.143 'cp /opt/ayala-backend/ayala_app.db /backup/ayala_app_$(date +%Y%m%d).db'
```

---

## 🎯 Next Steps

1. **Deploy**: Run `./deploy_to_server.sh` from `Ayala_app_back/ayala-backend/`
2. **Test**: Try registration from iOS app
3. **Monitor**: Check logs for any issues
4. **Scale**: Consider adding HTTPS and database backup

Your server setup will be production-ready with proper password hashing and secure API endpoints! 🛡️ 