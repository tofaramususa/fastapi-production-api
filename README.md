# Production API Service

A high-performance, production-ready API service built with **FastAPI** and **MongoDB**, designed for scalable enterprise applications with comprehensive security, monitoring, and performance optimization features.

## 🚀 Features

### Core Architecture
- **FastAPI Framework**: High-performance async web framework with automatic OpenAPI documentation
- **MongoDB Integration**: Async MongoDB operations using Motor and ODMantic ODM
- **Microservices Ready**: Containerized with Docker for easy deployment and scaling
- **Python 3.11+**: Modern Python with full type hints and async/await support

### 🔐 Security & Authentication
- **Firebase Authentication**: Secure user authentication with Firebase integration
- **JWT Token Management**: Access and refresh token handling with configurable expiration
- **Master Token Access**: Administrative access for system operations
- **Role-Based Access Control**: Admin and user role differentiation with domain-based admin detection
- **Resource-Level Permissions**: Granular folder and product access control
- **CORS Configuration**: Configurable cross-origin resource sharing with security controls

### 🛡️ Rate Limiting & Performance
- **Advanced Rate Limiting**: Redis-based rate limiting with Upstash integration
  - Default user limits: 100 requests/minute
  - Admin limits: 10,000 requests/minute  
  - Product creation limits: 1 creation per 2 hours
- **Sliding Window Algorithm**: Precise rate limiting with sliding window implementation
- **Per-User & IP-Based Limiting**: Flexible rate limiting strategies
- **Graceful Degradation**: Continues operation even if Redis is unavailable

### 📊 Monitoring & Observability
- **Sentry Integration**: Comprehensive error tracking and performance monitoring
  - 100% transaction sampling in production
  - Continuous profiling for performance insights
  - PII data collection for debugging
- **Logging**: JSON-formatted logs with configurable levels
- **Health Checks**: Database connectivity monitoring with retry logic

### 🗄️ Database & Data Management
- **MongoDB with ODMantic**: Modern async ODM for MongoDB operations
- **Connection Pooling**: Efficient database connection management
- **Migration Support**: Database migration scripts and version control
- **Data Models**: Well-structured Pydantic models for data validation
  - User management
  - Folder and product organization
  - Permission management

### 🔧 Development & Operations
- **Environment Configuration**: Comprehensive settings management with Pydantic Settings
- **Docker Containerization**: Production-ready Docker setup with multi-stage builds
- **Development Tools**: 
  - Black code formatting
  - isort import sorting
  - MyPy type checking
  - Pytest testing framework
- **Pre-commit Hooks**: Code quality enforcement
- **Hatch Build System**: Modern Python project management

### 📧 Communication & Notifications
- **Email Integration**: SMTP configuration for transactional emails
- **Template Support**: Jinja2 templating for dynamic content
- **Celery Task Queue**: Asynchronous task processing for background jobs

### 🌐 API Features
- **RESTful Design**: Clean, intuitive API endpoints
- **Automatic Documentation**: Interactive Swagger UI and ReDoc
- **Request Validation**: Comprehensive input validation with Pydantic
- **Response Schemas**: Structured API responses with type safety
- **Error Handling**: Standardized error responses with proper HTTP status codes
- **API Versioning**: Versioned endpoints for backward compatibility

### 🔄 Background Processing
- **APScheduler Integration**: MongoDB-backed job scheduling
- **Configurable Workers**: Scalable background task processing
- **Cleanup Jobs**: Automatic maintenance and cleanup operations
- **Production Scheduling**: Environment-aware scheduler initialization

## 🛠️ Technology Stack

### Core Dependencies
- **FastAPI**: Modern, fast web framework for building APIs
- **Motor**: Async MongoDB driver for Python
- **ODMantic**: MongoDB ODM with Pydantic integration
- **Pydantic v2**: Data validation and settings management
- **Uvicorn**: ASGI server for production deployment

### Security & Authentication
- **Firebase Admin SDK**: User authentication and management
- **python-jose**: JWT token handling with cryptographic support
- **Argon2**: Secure password hashing

### Performance & Caching
- **Upstash Redis**: Serverless Redis for rate limiting and caching
- **Tenacity**: Retry logic for resilient operations

### Monitoring & Logging
- **Sentry SDK**: Error tracking and performance monitoring
- **Prometheus Client**: Metrics collection and monitoring

### Development Tools
- **Pytest**: Testing framework with async support
- **Black**: Code formatting
- **MyPy**: Static type checking
- **isort**: Import sorting

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MongoDB instance
- Redis instance (optional, for rate limiting)
- Firebase project (for authentication)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd production-api
   ```

2. **Install dependencies**
   ```bash
   pip install hatch
   hatch env create
   ```

3. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize the database**
   ```bash
   python app/backend_pre_start.py
   ```

5. **Run the development server**
   ```bash
   hatch run uvicorn app.main:app --reload
   ```

### Docker Deployment

```bash
# Build the image
docker build -t production-api .

# Run the container
docker run -p 8000:8000 production-api
```

## 📋 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_DATABASE_URI` | MongoDB connection string | Required |
| `MONGO_DATABASE` | Database name | Required |
| `SECRET_KEY` | JWT secret key | Auto-generated |
| `FIREBASE_CREDENTIALS` | Firebase service account JSON | Required |
| `SENTRY_DSN` | Sentry monitoring URL | Optional |
| `UPSTASH_REDIS_REST_URL` | Redis URL for rate limiting | Optional |
| `RATE_LIMIT_DEFAULT` | Default rate limit per minute | 100 |
| `PRODUCTION` | Production mode flag | false |

### Rate Limiting Configuration

```python
# Default user limits
RATE_LIMIT_DEFAULT = 100  # requests per minute
RATE_LIMIT_WINDOW = 60    # seconds

# Admin user limits  
RATE_LIMIT_ADMIN = 10000  # requests per minute

# Product creation limits
RATE_LIMIT_PRODUCT_CREATION_MAX = 1     # products
RATE_LIMIT_PRODUCT_CREATION_WINDOW = 7200  # 2 hours
```

## 📚 API Documentation

When running in development mode, interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

### Authentication

All endpoints require authentication via Bearer token:

```bash
curl -H "Authorization: Bearer <your-token>" \
     http://localhost:8000/api/v1/endpoint
```

### Rate Limiting Headers

API responses include rate limiting information:

```json
{
  "X-RateLimit-Limit": "100",
  "X-RateLimit-Remaining": "95", 
  "X-RateLimit-Reset": "1640995200"
}
```

## 🧪 Testing

```bash
# Run all tests
hatch run pytest

# Run with coverage
hatch run pytest --cov=app

# Run specific test file
hatch run pytest tests/test_auth.py
```

## 🔍 Code Quality

```bash
# Format code
hatch run lint:fmt

# Check style
hatch run lint:style

# Type checking
hatch run mypy app/
```

## 📈 Monitoring

### Metrics
The API exposes Prometheus metrics for monitoring:
- Request duration and count
- Rate limit violations
- Database connection status
- Error rates by endpoint

### Error Tracking
Sentry integration provides:
- Real-time error notifications
- Performance monitoring
- Release tracking
- User impact analysis

## 🚀 Production Deployment

### Docker Compose Example

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PRODUCTION=true
      - MONGO_DATABASE_URI=mongodb://mongo:27017
    depends_on:
      - mongo
      - redis
  
  mongo:
    image: mongo:7
    volumes:
      - mongo_data:/data/db
  
  redis:
    image: redis:alpine
    
volumes:
  mongo_data:
```

### Performance Tuning

- **Workers**: Configure `MAX_WORKERS` based on CPU cores
- **Connection Pooling**: Adjust MongoDB connection pool size
- **Rate Limits**: Tune rate limits based on usage patterns
- **Caching**: Implement Redis caching for frequently accessed data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation
- Review the configuration guide

---

**Built with ❤️ using FastAPI and MongoDB for high-performance, scalable API services.**
