# Ayala Foundation Backend API

A FastAPI-based backend service for the Ayala Foundation charity fund management system. This API helps charity funds discover companies and their relevant data based on geographical location and AI-powered natural language input.

## 🏗️ Architecture

- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Primary database with PostGIS for geographic queries
- **Redis**: Caching layer for improved performance
- **Docker**: Containerization for consistent deployment
- **Alembic**: Database migration management

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Server with minimum 2GB RAM and 20GB disk space

### Automated Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Ayala_app_back
```

2. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

3. The application will be available at:
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

### Manual Setup

If you prefer manual setup:

```bash
# Create environment file
cp back/.env.example back/.env
# Edit back/.env with your configuration

# Build and start all services
docker-compose up -d

# Run database migrations
docker-compose exec api alembic upgrade head
```

## 🔧 Configuration

### Environment Variables

The setup script creates a `.env` file in the `back/` directory. Update it for production:

```env
# Database Configuration
POSTGRES_SERVER=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=ayala_foundation
POSTGRES_PORT=5432

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Security (CHANGE THESE!)
SECRET_KEY=your-super-secure-secret-key
JWT_SECRET_KEY=your-super-secure-jwt-key

# OpenAI Configuration (optional)
OPENAI_API_KEY=your-openai-api-key-here

# Application Settings
PROJECT_NAME=Ayala Foundation API
VERSION=1.0.0
```

### Database Connection

The application connects to PostgreSQL running in Docker with these settings:
- **Host**: postgres (container name)
- **Port**: 5432
- **Username**: postgres
- **Database**: ayala_foundation

## 📊 Database

### Migrations

The project uses Alembic for database migrations:

```bash
# Create a new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback migration
docker-compose exec api alembic downgrade -1
```

### Schema

Key tables:
- `users`: User authentication and profiles
- `funds`: Charity fund information
- `companies`: Company data with location and contact info
- `locations`: Geographic data for companies

## 🌐 API Endpoints

### Authentication
- `POST /api/v1/auth/token` - Login
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/password-reset-request` - Request password reset
- `POST /api/v1/auth/password-reset` - Reset password

### Fund Management
- `POST /api/v1/funds/profile` - Create fund profile
- `GET /api/v1/funds/profile` - Get fund profile
- `POST /api/v1/funds/conversation` - AI conversation for fund setup

### Company Search
- `GET /api/v1/companies/search` - Search companies
- `GET /api/v1/companies/{id}` - Get company details
- `GET /api/v1/companies/region/{region}` - Get companies by region
- `GET /api/v1/companies/suggest` - AI-powered company suggestions

### Health Check
- `GET /api/v1/health` - Service health status

## 🔄 Caching

Redis is used for caching to improve performance:

- **Company search results**: Cached for 1 hour
- **Geographic queries**: Cached for 2 hours
- **AI suggestions**: Cached for 30 minutes

Cache keys follow the pattern: `{feature}:{hash_of_parameters}`

## 🧪 Testing

Run tests using Docker:

```bash
# Run tests inside container
docker-compose exec api pytest

# Run with coverage
docker-compose exec api pytest --cov=src tests/
```

## 📦 Production Deployment

### With Nginx (Recommended)

```bash
# Start with Nginx reverse proxy
docker-compose --profile production up -d
```

This includes:
- Nginx reverse proxy on port 80
- SSL termination support
- Production-optimized settings

### Server Requirements

- **CPU**: 2+ cores
- **RAM**: 4GB+ recommended
- **Disk**: 20GB+ SSD
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **Ports**: 80, 443, 8000

### SSL Setup

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- Environment variable configuration
- CORS protection
- Security headers via Nginx
- **⚠️ Change default passwords and secret keys in production!**

## 📈 Monitoring & Management

### Health Checks

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f api

# Check resource usage
docker stats
```

### Database Backup

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres ayala_foundation > backup_$(date +%Y%m%d).sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U postgres ayala_foundation
```

### Common Commands

```bash
# Restart API service
docker-compose restart api

# Update application
git pull
docker-compose build api
docker-compose up -d

# View application logs
docker-compose logs -f api

# Scale API instances
docker-compose up -d --scale api=3
```

## 🗂️ Project Structure

```
Ayala_app_back/
├── back/
│   ├── src/
│   │   ├── auth/          # Authentication module
│   │   ├── companies/     # Company management
│   │   ├── funds/         # Fund management
│   │   ├── core/          # Core utilities
│   │   └── main.py        # FastAPI application
│   ├── migrations/        # Database migrations
│   ├── parser/           # Data parsing utilities
│   ├── Dockerfile        # Container definition
│   └── requirements.txt  # Python dependencies
├── docker-compose.yml    # Docker services configuration
├── nginx.conf           # Nginx configuration
├── setup.sh             # Automated setup script
└── README.md           # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `docker-compose exec api pytest`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Docker Documentation](https://docs.docker.com/) 