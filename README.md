# Take Note Backend API

A robust and scalable backend API for the Take Note mobile application, built with FastAPI and Supabase. This API provides secure note management capabilities with features like authentication, CRUD operations, search, pinning, and soft delete with undo functionality.

## 🚀 Features

- **Authentication & Authorization**: Secure user authentication using Supabase Auth with JWT tokens
- **Notes CRUD Operations**: Create, read, update, and delete notes with full validation
- **Search & Filter**: Powerful search functionality across note titles and content
- **Pin/Favorite Notes**: Mark important notes to keep them at the top
- **Soft Delete with Undo**: Delete notes with ability to restore them
- **Offline-First Architecture**: Designed to work seamlessly with offline-capable mobile apps
- **Rate Limiting**: Built-in protection against abuse
- **Security Headers**: Comprehensive security middleware
- **Input Validation**: Robust validation using Pydantic models
- **Error Handling**: Detailed error responses with proper HTTP status codes
- **Database Optimization**: Indexed queries for optimal performance

## 🏗️ Architecture

The API follows a clean architecture pattern with clear separation of concerns:

```
├── main.py              # FastAPI application and endpoints
├── config.py            # Configuration management
├── database.py          # Database operations and Supabase integration
├── models.py            # Pydantic models for request/response validation
├── auth.py              # Authentication and authorization
├── security.py          # Security middleware and utilities
├── exceptions.py        # Custom exceptions and error handlers
├── schemas.sql          # Database schema and migrations
├── test_main.py         # Comprehensive test suite
├── requirements.txt     # Python dependencies
└── env.example          # Environment variables template
```

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python 3.8+)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth with JWT
- **Validation**: Pydantic
- **Testing**: Pytest
- **Security**: JWT tokens, rate limiting, security headers

## 📋 Prerequisites

- Python 3.8 or higher
- Supabase account and project
- pip or pipenv for package management

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd take-note-backend
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Setup

Copy the environment template and configure your variables:

```bash
cp env.example .env
```

Edit `.env` with your Supabase credentials:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
APP_NAME=Take Note Backend API
APP_VERSION=1.0.0
DEBUG=True
```

### 4. Database Setup

Run the SQL schema in your Supabase project:

```bash
# Execute the contents of schemas.sql in your Supabase SQL editor
```

### 5. Run the Application

```bash
# Development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Core Endpoints

#### Authentication
All endpoints (except `/` and `/health`) require authentication via Bearer token in the Authorization header.

#### Notes Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/notes` | Get all user notes with pagination | ✅ |
| POST | `/notes` | Create a new note | ✅ |
| GET | `/notes/{id}` | Get a specific note | ✅ |
| PUT | `/notes/{id}` | Update a note | ✅ |
| DELETE | `/notes/{id}` | Soft delete a note | ✅ |
| PATCH | `/notes/{id}/pin` | Toggle pin status | ✅ |
| POST | `/notes/{id}/restore` | Restore deleted note | ✅ |
| POST | `/notes/search` | Search notes | ✅ |

#### System Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | API information | ❌ |
| GET | `/health` | Health check | ❌ |

### Request/Response Examples

#### Create a Note

```bash
curl -X POST "http://localhost:8000/notes" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Note",
    "content": "This is the content of my note",
    "is_pinned": false
  }'
```

Response:
```json
{
  "id": "uuid-here",
  "user_id": "user-uuid",
  "title": "My First Note",
  "content": "This is the content of my note",
  "is_pinned": false,
  "is_deleted": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null,
  "deleted_at": null
}
```

#### Get Notes with Pagination

```bash
curl -X GET "http://localhost:8000/notes?page=1&size=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Response:
```json
{
  "notes": [...],
  "total": 25,
  "page": 1,
  "size": 10
}
```

#### Search Notes

```bash
curl -X POST "http://localhost:8000/notes/search" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "important",
    "limit": 20
  }'
```

## 🔒 Security Features

### Authentication
- JWT token-based authentication via Supabase Auth
- Token verification for all protected endpoints
- Automatic token expiration handling

### Authorization
- User isolation: Users can only access their own notes
- Row-level security (RLS) policies in the database
- Resource ownership validation

### Input Validation
- Comprehensive request validation using Pydantic
- SQL injection prevention
- XSS protection
- Request size limiting

### Rate Limiting
- Configurable rate limiting per IP address
- Prevents API abuse and DoS attacks
- Automatic cleanup of old rate limit data

### Security Headers
- Content Security Policy (CSP)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection
- Strict-Transport-Security (HTTPS only)

## 🧪 Testing

Run the comprehensive test suite:

```bash

pytest


pytest --cov=main --cov-report=html


pytest test_main.py -v
```

The test suite includes:
- Unit tests for all endpoints
- Authentication testing
- Error handling validation
- Input validation testing
- Pagination testing
- Search functionality testing

## 🚀 Deployment

### Environment Variables for Production

```env
DEBUG=False
JWT_SECRET_KEY=your-very-secure-secret-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t take-note-backend .
docker run -p 8000:8000 --env-file .env take-note-backend
```

### Production Considerations

1. **Database Connection Pooling**: Configure Supabase connection limits
2. **Monitoring**: Implement logging and monitoring
3. **Backup Strategy**: Regular database backups
4. **SSL/TLS**: Use HTTPS in production
5. **Load Balancing**: Consider load balancer for high traffic

## 🤝 API Integration with Flutter

This backend is designed to work seamlessly with the Flutter mobile app. Key integration points:

### Authentication Flow
1. User signs up/logs in via Supabase Auth
2. Flutter app receives JWT token
3. Include token in Authorization header for all API calls

### Offline-First Strategy
- Flutter app caches notes locally using SQLite/Hive
- Sync with backend when online
- Handle conflicts gracefully

### Error Handling
- All errors return structured JSON responses
- Flutter app can parse and display user-friendly messages
- Network error handling for offline scenarios

## 📈 Performance Optimization

### Database Optimizations
- Indexed columns for fast queries
- Full-text search capabilities
- Efficient pagination
- Soft delete to maintain referential integrity

### API Optimizations
- Connection pooling
- Async/await throughout
- Efficient serialization
- Minimal response payloads

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SUPABASE_URL` | Supabase project URL | ✅ | - |
| `SUPABASE_KEY` | Supabase anon key | ✅ | - |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | ❌ | - |
| `JWT_SECRET_KEY` | JWT signing secret | ✅ | - |
| `JWT_ALGORITHM` | JWT algorithm | ❌ | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | ❌ | 30 |
| `DEBUG` | Debug mode | ❌ | True |

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify Supabase URL and keys
   - Check network connectivity
   - Ensure database is accessible

2. **Authentication Errors**
   - Verify JWT token is valid
   - Check token expiration
   - Ensure proper Authorization header format

3. **Rate Limiting**
   - Reduce request frequency
   - Implement proper retry logic
   - Consider increasing rate limits for production

---

**Built with ❤️ for the Take Note mobile application**
