# Pukaar-GPT: AI-Powered Infant Health Screening Tool

An intelligent infant health screening application that uses AI models based on WHO, IMNCI, and IAP guidelines to provide triage, red flag detection, context classification, and consultation advice.

## 🏥 Features

- **AI-Powered Triage**: Intelligent symptom analysis and triage recommendations
- **Red Flag Detection**: Automatic detection of critical symptoms requiring immediate attention
- **Context Classification**: Smart categorization of health concerns
- **Consultation Advice**: Evidence-based recommendations for next steps
- **WHO/IMNCI/IAP Compliant**: Based on international pediatric guidelines
- **Modern Web Interface**: React-based frontend with intuitive UX

## 🏗️ Architecture

- **Backend**: Flask API with Google Generative AI (Gemini) integration
- **Frontend**: React application with modern UI/UX
- **AI Models**: Google's Gemini for natural language processing
- **Deployment**: Docker containerization with multi-environment support

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Google API Key for Gemini AI
- Linux/macOS/Windows with Docker support

### 1. Environment Setup

Create a `.env` file in the project root:

```bash
# Google API Configuration
GOOGLE_API_KEY=your-google-api-key-here

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=production

# Frontend Configuration
REACT_APP_API_URL=http://34.47.240.92:5000
```

### 2. Choose Your Deployment Method

#### 🚀 **Quick Development Build** (Fastest for Recent Changes)
```bash
./build_dev.sh
```
- ⚡ Fastest option when images are recent (< 10 minutes)
- Skips build if recent images exist
- Uses Docker layer caching when building
- Perfect for frequent code changes

#### 🧠 **Smart Incremental Build** (Recommended)
```bash
./build_incremental.sh
```
- 🎯 Only rebuilds changed components
- Uses file change detection
- 70-80% faster than full rebuilds
- Best for development and testing

#### 🏠 **Local Development** (Isolated)
```bash
./run_local.sh
```
- 🔒 Isolated from production containers
- Uses localhost URLs
- Safe for development without affecting production

#### 🌐 **Production Deployment**
```bash
./run_prod.sh
```
- 🏭 Production-optimized configuration
- Uses external IP addresses
- Includes health checks and monitoring

#### 📦 **Full Production Deployment**
```bash
./deploy.sh
```
- 🔧 Complete deployment with all checks
- Comprehensive error handling
- Production-ready with all optimizations

## 🛠️ Build System

### Incremental Build Features

Our build system uses intelligent caching to dramatically reduce build times:

#### **File Change Detection**
- MD5 hash-based change detection
- Only rebuilds components with actual changes
- Tracks backend (Python) and frontend (JavaScript/React) separately

#### **Docker Layer Caching**
- Optimized Dockerfiles for maximum layer reuse
- Separate layers for dependencies vs. source code
- Multi-stage builds for efficient image creation

#### **Build Performance**

| Build Type | Time | Use Case |
|------------|------|----------|
| **Full Rebuild** | 3-5 minutes | Initial setup, dependency changes |
| **Incremental** | 30s - 2 minutes | Code changes, development |
| **Quick Dev** | 10s - 2 minutes | Recent changes, frequent development |

### Build Scripts Overview

| Script | Purpose | Best For |
|--------|---------|----------|
| `build_dev.sh` | Quick dev builds (recent images) | Daily development |
| `build_incremental.sh` | Smart incremental builds | Testing and staging |
| `run_local.sh` | Local development environment | Isolated development |
| `run_prod.sh` | Production environment | Production deployment |
| `deploy.sh` | Full production deployment | Complete deployment |

### Build Speed Comparison

**`build_dev.sh`** - Fastest for recent changes:
- ⚡ **10 seconds** if images are recent (< 10 minutes old)
- 🔄 **1-2 minutes** if images need rebuilding
- 🎯 **Best for**: Frequent development cycles

**`build_incremental.sh`** - Smartest for code changes:
- 🧠 **30 seconds - 2 minutes** depending on what changed
- 📊 **File change detection** - only rebuilds what's necessary
- 🎯 **Best for**: When you've made code changes

**`run_local.sh` / `run_prod.sh`** - Standard builds:
- ⏱️ **2-3 minutes** for full build with caching
- 🔧 **Standard Docker layer caching**
- 🎯 **Best for**: Regular development and production

## 🔧 Advanced Usage

### Force Full Rebuild
```bash
# Remove build cache and rebuild everything
rm .last_*_build && ./build_incremental.sh

# Or use --no-cache flag
docker-compose build --no-cache
```

### View Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Container Management
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild specific service
docker-compose build backend
docker-compose build frontend
```

### Environment-Specific Commands

#### Local Development
```bash
# Start local environment
./run_local.sh

# View local logs
docker-compose -f docker-compose.local.yml -p pukaar-local logs -f

# Stop local environment
docker-compose -f docker-compose.local.yml -p pukaar-local down
```

#### Production
```bash
# Start production environment
./run_prod.sh

# View production logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop production environment
docker-compose -f docker-compose.prod.yml down
```

## 📁 Project Structure

```
Pukaar-GPT/
├── backend/                 # Flask API backend
│   ├── app.py              # Main Flask application
│   ├── models.py           # AI model integrations
│   ├── utils.py            # Utility functions
│   ├── config.py           # Configuration management
│   ├── req.txt             # Python dependencies
│   └── templates/          # API documentation templates
├── frontend/               # React frontend
│   ├── src/                # React source code
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
├── docker-compose.yml      # Main Docker Compose configuration
├── docker-compose.prod.yml # Production configuration
├── docker-compose.local.yml # Local development configuration
├── Dockerfile.backend      # Backend container definition
├── Dockerfile.frontend     # Frontend container definition
├── .dockerignore           # Docker build exclusions
├── .env                    # Environment variables (create this)
├── build_incremental.sh    # Smart incremental build script
├── build_dev.sh           # Quick development build script
├── run_local.sh           # Local development runner
├── run_prod.sh            # Production runner
├── deploy.sh              # Full deployment script
└── README.md              # This file
```

## 🔑 Environment Variables

### Required
- `GOOGLE_API_KEY`: Your Google API key for Gemini AI access

### Optional
- `FLASK_ENV`: Environment mode (development/production)
- `REACT_APP_API_URL`: Frontend API endpoint URL

## 🌐 API Endpoints

- **Frontend**: http://localhost:3000 (local) / http://34.47.240.92:3000 (production)
- **Backend API**: http://localhost:5000 (local) / http://34.47.240.92:5000 (production)
- **API Documentation**: http://localhost:5000/api-doc (local) / http://34.47.240.92:5000/api-doc (production)

## 🚨 Troubleshooting

### Common Issues

#### Build Failures
```bash
# Clean Docker cache
docker system prune -f

# Force rebuild
docker-compose build --no-cache
```

#### Container Issues
```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs [service-name]
```

#### Disk Space Issues
```bash
# Clean up Docker resources
docker system prune -a -f

# Check disk usage
df -h
```

### Performance Optimization

1. **Use incremental builds** for development
2. **Clean Docker cache** regularly
3. **Monitor disk space** during builds
4. **Use appropriate build script** for your use case

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with incremental builds
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Check container logs for errors
4. Ensure environment variables are properly set

---

**Pukaar-GPT**: Empowering healthcare providers with AI-driven infant health screening.