# AI Chatbot Service

A sophisticated, production-ready AI chatbot service built with FastAPI, PostgreSQL, Redis, and Ollama. This service provides real-time chat capabilities with context-aware responses, multi-language support, and seamless website integration.

## 🌟 Features

### Core Functionality
- Real-time chat via WebSocket connections
- Context-aware responses based on website content
- Multi-language support with automatic language detection
- Response caching for improved performance
- Rate limiting and usage tracking
- Comprehensive API documentation

### Technical Features
- Asynchronous API design with FastAPI
- PostgreSQL database with async SQLAlchemy
- Redis for caching and rate limiting
- Docker containerization for development and production
- CI/CD pipeline with GitHub Actions
- AWS ECS deployment support
- Comprehensive test coverage
- API key authentication
- WebSocket support for real-time communication

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Poetry (Python package manager)

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/AlbinisRudaku/emmy.git
cd emmy
```
2. Run the development setup script:
** Windows **
```powershell
.\scripts\init-dev.ps1
```
** Linux/MacOS **
```bash
chmod +x scripts/init-dev.sh
./scripts/init-dev.sh
```
The setup script will:
- Create a `.env` file from `.env.example`
- Start Docker containers
- Run database migrations
- Create initial test data

### Manual Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source venv/bin/activate # Linux/MacOS
.\venv\Scripts\activate # Windows
```
2. Install dependencies:
```bash
poetry install
```
3. Start the development environment:
```bash
docker-compose -f docker-compose.dev.yml up -d
```
4. Run migrations:
```bash
poetry run alembic upgrade head
```

## 🏗️ Project Structure

```bash
ai-chatbot-service/
├── app/
│ ├── api/ # API routes and endpoints
│ ├── core/ # Core functionality and config
│ ├── models/ # Pydantic and database models
│ └── services/ # Business logic
├── alembic/ # Database migrations
├── scripts/ # Utility scripts
├── tests/ # Test suite
└── docker/ # Docker configuration
```

## 🔧 Configuration
Configuration is managed through environment variables and the `.env` file. Key configuration options:
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/chatbot
REDIS_URL=redis://redis:6379
OLLAMA_BASE_URL=http://ollama:11434
DEBUG=True
SECRET_KEY=your-secret-key-here
```

## 📚 API Documentation

Once running, API documentation is available at:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`
- OpenAPI JSON: `http://localhost:8000/api/v1/openapi.json`

### Key Endpoints

- **Authentication:**
  - `POST /api/v1/auth/register` - Register new user
  - `POST /api/v1/auth/login` - Login and get access token

- **Chat:**
  - `POST /api/v1/chat/message` - Send a chat message
  - `WS /api/v1/chat/ws/{instance_id}` - WebSocket endpoint for real-time chat

- **Instance Management:**
  - `POST /api/v1/instances` - Create new chatbot instance
  - `GET /api/v1/instances` - List all instances

## 🔒 Security

- API key authentication for all endpoints
- Rate limiting per API key
- JWT-based user authentication
- Secure WebSocket connections
- Input validation and sanitization
- CORS configuration
- Environment variable management

## 🧪 Testing
Run the test suite:
```bash
poetry run pytest --cov=app --cov-report=html
```

## 🚀 Deployment

### Docker Production Deployment

1. Build the production image:
```bash
docker build -t ai-chatbot-service .
```
2. Run with production configuration:
```bash
docker-compose up -d
```

### AWS Deployment

The service includes GitHub Actions workflows for automated deployment to AWS ECS:

1. Configure AWS credentials in GitHub secrets
2. Push to main branch to trigger deployment
3. Service will be deployed to ECS with auto-scaling

## 📈 Monitoring

- Health check endpoint: `/health`
- Prometheus metrics
- JSON logging with correlation IDs
- Performance monitoring
- Rate limit tracking

---

Built with ❤️ using FastAPI, PostgreSQL, Redis, and Ollama
