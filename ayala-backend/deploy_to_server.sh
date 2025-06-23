#!/bin/bash

# Ayala Foundation Backend Deployment Script
# Deploy to: 142.93.103.143

SERVER_IP="142.93.103.143"
SERVER_USER="root"  # Change if you use a different user
APP_NAME="ayala-backend"
REMOTE_DIR="/opt/ayala-backend"
DOMAIN="api.ayala.kz"  # Change this to your actual domain

echo "🚀 Deploying Ayala Foundation Backend to $SERVER_IP"
echo "=================================================="

# Function to run commands on remote server with error checking
run_remote() {
    echo "Executing: $1"
    ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "$1"
    if [ $? -ne 0 ]; then
        echo "❌ Remote command failed: $1"
        return 1
    fi
    return 0
}

# Function to copy files to remote server with error checking
copy_to_remote() {
    echo "Copying: $1 -> $2"
    scp -o StrictHostKeyChecking=no -r "$1" $SERVER_USER@$SERVER_IP:"$2"
    if [ $? -ne 0 ]; then
        echo "❌ File copy failed: $1 -> $2"
        return 1
    fi
    return 0
}

echo "📋 Step 1: Checking server connectivity..."
if ! ping -c 1 $SERVER_IP > /dev/null 2>&1; then
    echo "❌ Cannot reach server $SERVER_IP"
    echo "💡 Make sure:"
    echo "   - Server is running"
    echo "   - Firewall allows SSH (port 22)"
    echo "   - You have SSH access"
    exit 1
fi

echo "✅ Server is reachable"

echo "📋 Step 2: Testing SSH connection..."
if ! ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 $SERVER_USER@$SERVER_IP "echo 'SSH connection successful'" 2>/dev/null; then
    echo "❌ SSH connection failed"
    echo "💡 Make sure:"
    echo "   - You have SSH key access OR password access"
    echo "   - User '$SERVER_USER' exists on the server"
    echo "   - SSH service is running on the server"
    exit 1
fi

echo "✅ SSH connection successful"

echo "📋 Step 3: Installing system dependencies..."
if ! run_remote "apt-get update && apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx ufw"; then
    echo "❌ Failed to install system dependencies"
    exit 1
fi

echo "📋 Step 4: Preparing remote directory..."
if ! run_remote "mkdir -p $REMOTE_DIR"; then
    echo "❌ Failed to create remote directory"
    exit 1
fi

if ! run_remote "chmod 755 $REMOTE_DIR"; then
    echo "❌ Failed to set directory permissions"
    exit 1
fi

echo "📋 Step 5: Cleaning existing files..."
run_remote "rm -rf $REMOTE_DIR/*" || echo "Directory was empty or clean failed (non-critical)"

echo "📋 Step 6: Copying application files..."

# Copy source directory
if ! copy_to_remote "src/" "$REMOTE_DIR/"; then
    echo "❌ Failed to copy src/ directory"
    exit 1
fi

# Copy requirements.txt
if ! copy_to_remote "requirements.txt" "$REMOTE_DIR/"; then
    echo "❌ Failed to copy requirements.txt"
    exit 1
fi

# Copy alembic.ini
if ! copy_to_remote "alembic.ini" "$REMOTE_DIR/"; then
    echo "❌ Failed to copy alembic.ini"
    exit 1
fi

# Copy .env file if it exists
if [ -f ".env" ]; then
    copy_to_remote ".env" "$REMOTE_DIR/" || echo "⚠️  .env copy failed (will create default)"
else
    echo "ℹ️  No .env file found locally (will create default)"
fi

echo "📋 Step 7: Setting up Python virtual environment..."
if ! run_remote "cd $REMOTE_DIR && python3 -m venv venv"; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

if ! run_remote "cd $REMOTE_DIR && source venv/bin/activate && pip install --upgrade pip"; then
    echo "❌ Failed to upgrade pip"
    exit 1
fi

echo "📋 Step 8: Installing Python dependencies..."
if ! run_remote "cd $REMOTE_DIR && source venv/bin/activate && pip install -r requirements.txt"; then
    echo "❌ Failed to install Python dependencies"
    echo "💡 Check if requirements.txt is valid"
    exit 1
fi

echo "📋 Step 9: Setting up environment configuration..."
run_remote "cd $REMOTE_DIR && cat > .env << 'EOF'
DATABASE_URL=sqlite:///./ayala_app.db
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-$(date +%s)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
APP_NAME=Ayala Foundation API
DEBUG=False
ALLOWED_ORIGINS=[\"https://$DOMAIN\", \"https://www.$DOMAIN\"]
EOF"

echo "📋 Step 10: Setting up systemd service..."
run_remote "cat > /etc/systemd/system/ayala-backend.service << 'EOF'
[Unit]
Description=Ayala Foundation Backend API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$REMOTE_DIR
Environment=PATH=$REMOTE_DIR/venv/bin
ExecStart=$REMOTE_DIR/venv/bin/uvicorn src.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

echo "📋 Step 11: Setting up Nginx configuration..."
run_remote "cat > /etc/nginx/sites-available/ayala-backend << 'EOF'
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN $SERVER_IP;

    # Allow Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/html;
        allow all;
    }

    # Redirect HTTP to HTTPS (will be enabled after SSL setup)
    # return 301 https://\$server_name\$request_uri;

    # Temporarily serve the API over HTTP for initial setup
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Serve API docs
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Serve OpenAPI spec
    location /openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF"

echo "📋 Step 12: Enabling Nginx configuration..."
run_remote "rm -f /etc/nginx/sites-enabled/default"
run_remote "ln -sf /etc/nginx/sites-available/ayala-backend /etc/nginx/sites-enabled/"
run_remote "nginx -t"

echo "📋 Step 13: Configuring firewall..."
run_remote "ufw --force enable"
run_remote "ufw allow 22/tcp"    # SSH
run_remote "ufw allow 80/tcp"    # HTTP
run_remote "ufw allow 443/tcp"   # HTTPS

echo "📋 Step 14: Starting services..."
if ! run_remote "systemctl daemon-reload"; then
    echo "❌ Failed to reload systemd"
    exit 1
fi

if ! run_remote "systemctl enable ayala-backend"; then
    echo "❌ Failed to enable service"
    exit 1
fi

# Stop any existing service
run_remote "systemctl stop ayala-backend" || echo "Service was not running (normal for first deploy)"

if ! run_remote "systemctl start ayala-backend"; then
    echo "❌ Failed to start service"
    echo "🔍 Checking logs..."
    run_remote "journalctl -u ayala-backend -n 20 --no-pager"
    exit 1
fi

if ! run_remote "systemctl restart nginx"; then
    echo "❌ Failed to start nginx"
    exit 1
fi

echo "📋 Step 15: Setting up SSL certificates..."
echo "🔧 If you have a domain configured, we'll set up SSL automatically"
echo "   Domain: $DOMAIN"
echo "   Make sure your domain points to $SERVER_IP before proceeding"

read -p "Do you want to set up SSL certificates now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔐 Setting up SSL with Let's Encrypt..."
    if run_remote "certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN"; then
        echo "✅ SSL certificates installed successfully!"
        
        # Update API configuration to use HTTPS
        echo "📋 Step 16: Updating API configuration for HTTPS..."
        # The certbot command above automatically updates nginx config for HTTPS
        
        echo "🎉 HTTPS DEPLOYMENT SUCCESSFUL!"
        echo "================================"
        echo ""
        echo "🌐 Your API is now available at:"
        echo "   📱 https://$DOMAIN/api/v1"
        echo "   📖 API Docs: https://$DOMAIN/docs"
        
    else
        echo "⚠️  SSL setup failed. Your API is available over HTTP:"
        echo "   📱 http://$SERVER_IP/api/v1"
        echo "   📖 API Docs: http://$SERVER_IP/docs"
        echo ""
        echo "💡 To set up SSL later, run:"
        echo "   ssh $SERVER_USER@$SERVER_IP 'certbot --nginx -d $DOMAIN'"
    fi
else
    echo "⚠️  SSL setup skipped. Your API is available over HTTP:"
    echo "   📱 http://$SERVER_IP/api/v1"
    echo "   📖 API Docs: http://$SERVER_IP/docs"
    echo ""
    echo "💡 To set up SSL later, run:"
    echo "   ssh $SERVER_USER@$SERVER_IP 'certbot --nginx -d $DOMAIN'"
fi

echo "📋 Step 17: Verifying deployment..."
sleep 5
SERVICE_STATUS=$(run_remote "systemctl is-active ayala-backend")
NGINX_STATUS=$(run_remote "systemctl is-active nginx")

if [ "$SERVICE_STATUS" = "active" ] && [ "$NGINX_STATUS" = "active" ]; then
    echo ""
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo "================================"
    echo ""
    echo "🔧 Management commands:"
    echo "   Start:   ssh $SERVER_USER@$SERVER_IP 'systemctl start ayala-backend'"
    echo "   Stop:    ssh $SERVER_USER@$SERVER_IP 'systemctl stop ayala-backend'"
    echo "   Restart: ssh $SERVER_USER@$SERVER_IP 'systemctl restart ayala-backend'"
    echo "   Logs:    ssh $SERVER_USER@$SERVER_IP 'journalctl -u ayala-backend -f'"
    echo "   Nginx:   ssh $SERVER_USER@$SERVER_IP 'systemctl restart nginx'"
    echo ""
    echo "🧪 Test your deployment:"
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   curl https://$DOMAIN/docs"
    else
        echo "   curl http://$SERVER_IP/docs"
    fi
    echo ""
    echo "✅ Your iOS app should now be able to connect!"
else
    echo ""
    echo "❌ DEPLOYMENT FAILED!"
    echo "====================="
    echo ""
    echo "Service status: $SERVICE_STATUS"
    echo "Nginx status: $NGINX_STATUS"
    echo ""
    echo "🔍 Check logs with:"
    echo "ssh $SERVER_USER@$SERVER_IP 'journalctl -u ayala-backend -n 50'"
    echo "ssh $SERVER_USER@$SERVER_IP 'journalctl -u nginx -n 50'"
    exit 1
fi 