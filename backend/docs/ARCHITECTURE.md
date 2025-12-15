# Backend Architecture Document

## Overview

IT Asset Management Platform backend built with Flask, following a modular MVC-like architecture with RESTful API design.

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Flask | 3.x |
| Database ORM | SQLAlchemy | via Flask-SQLAlchemy |
| Authentication | JWT | Flask-JWT-Extended |
| Validation | Marshmallow | Flask-Marshmallow |
| Migrations | Alembic | Flask-Migrate |
| CORS | Flask-CORS | - |

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # App factory & extensions init
│   ├── extensions.py         # Flask extension instances
│   ├── models/               # SQLAlchemy models
│   │   ├── __init__.py       # Model exports
│   │   ├── user.py           # User model
│   │   ├── server.py         # Server model
│   │   ├── container.py      # Container model
│   │   ├── service.py        # Service model
│   │   ├── gpu.py            # GPU model
│   │   ├── datacenter.py     # Datacenter model
│   │   ├── environment.py    # Environment model
│   │   └── audit_log.py      # Audit logging
│   ├── routes/               # API route blueprints
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── servers.py        # Server CRUD
│   │   ├── containers.py     # Container CRUD
│   │   ├── services.py       # Service CRUD
│   │   ├── gpus.py           # GPU CRUD + assignment
│   │   ├── datacenters.py    # Datacenter CRUD
│   │   ├── environments.py   # Environment list
│   │   ├── users.py          # User management
│   │   ├── audit_logs.py     # Audit log queries
│   │   ├── search.py         # Global search
│   │   └── import_export.py  # Data import/export
│   ├── schemas/              # Marshmallow validation schemas
│   │   └── __init__.py       # All validation schemas
│   └── utils/                # Utility functions
│       └── __init__.py       # Response helpers, decorators
├── config.py                 # Configuration classes
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
└── .env.example              # Environment template
```

## Data Model

### Entity Relationships

```
┌──────────────┐
│  Datacenter  │
└──────┬───────┘
       │ 1:N
       ▼
┌──────────────┐    ┌─────────────┐
│    Server    │◄───│ Environment │
└──────┬───────┘    └─────────────┘
       │ 1:N                │ 1:N
       ├────────────────────┘
       │
       ├───────────────┐
       ▼               ▼
┌──────────────┐ ┌──────────────┐
│  Container   │ │     GPU      │
└──────┬───────┘ └──────────────┘
       │ 1:N           │ N:1
       ▼               ▼
┌──────────────┐ ┌──────────────┐
│   Service    │ │     User     │
└──────────────┘ └──────────────┘
```

### Core Models

| Model | Description | Key Fields |
|-------|-------------|------------|
| User | System users | username, role, is_active |
| Datacenter | Physical locations | name, location |
| Environment | Deployment env | name, color (prod/staging/dev) |
| Server | Physical/virtual servers | name, IPs, specs, status |
| Container | Docker containers | name, image, limits, port_mappings |
| Service | Application services | name, type, port, health_check |
| GPU | Graphics cards | model, memory, assigned_to |
| AuditLog | Change tracking | action, resource_type, changes |

## API Design

### Authentication Flow

```
POST /api/auth/login    → Returns access_token + refresh_token
POST /api/auth/logout   → Client-side token removal
POST /api/auth/refresh  → Returns new access_token
GET  /api/auth/me       → Returns current user info
POST /api/auth/change-password → Update password
```

### RESTful Endpoints

All resource endpoints follow consistent patterns:

```
GET    /api/{resource}       → List with pagination & filters
GET    /api/{resource}/:id   → Get single resource
POST   /api/{resource}       → Create resource
PUT    /api/{resource}/:id   → Update resource
DELETE /api/{resource}/:id   → Delete resource
```

### Response Format

```json
{
  "code": 0,
  "message": "success",
  "data": { ... },
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "pages": 5
  }
}
```

### Error Responses

| HTTP Code | Business Code | Description |
|-----------|---------------|-------------|
| 400 | 400 | Bad request / validation error |
| 401 | 401 | Unauthorized / token expired |
| 403 | 403 | Forbidden / insufficient permissions |
| 404 | 404 | Resource not found |
| 422 | 422 | Validation failure |
| 500 | 500 | Internal server error |

## Security

### Authentication
- JWT-based authentication with access/refresh tokens
- Access tokens expire after configured duration
- Refresh tokens for seamless token renewal

### Authorization
- Role-based access control (admin/user)
- `@admin_required` decorator for admin-only endpoints
- Resource ownership checks for user-created resources

### Input Validation
- Marshmallow schemas validate all input data
- Type checking, length limits, format validation
- IP address format validation for network fields
- Enum validation for status fields

### Audit Logging
- All create/update/delete operations logged
- Captures user, action, changes, IP address
- Full resource snapshots on deletion

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| SECRET_KEY | Flask secret key | Yes |
| JWT_SECRET_KEY | JWT signing key | Yes |
| DATABASE_URL | Database connection string | Yes |
| FLASK_ENV | Environment (development/production) | No |
| CORS_ORIGINS | Allowed CORS origins | No |

### Configuration Classes

```python
Config           # Base configuration
DevelopmentConfig # Debug mode, SQLite fallback
ProductionConfig  # Production settings
TestingConfig     # Testing configuration
```

## Key Features

### Pagination
- Configurable page size (default: 20, max: 100)
- Returns total count and page info

### Filtering
- Query parameters for filtering lists
- Keyword search across multiple fields
- Status/type filters for categorization

### Tree View API
- `GET /api/servers/tree` returns hierarchical data
- Configurable expansion levels (1-3)
- Includes nested containers, services, GPUs

### GPU Assignment
- `POST /api/gpus/:id/assign` - Assign to user
- `POST /api/gpus/:id/release` - Release from user
- Tracks assignment status and history

### Import/Export
- Excel import for bulk data loading
- Data export for backup/migration

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your settings

# Initialize database
flask db upgrade
flask init-db  # Create initial data

# Run development server
flask run --debug
```

### Database Migrations

```bash
flask db migrate -m "Description"
flask db upgrade
flask db downgrade  # Rollback if needed
```

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app
```

## Performance Considerations

1. **Query Optimization**: Use eager loading for relationships
2. **Pagination**: Always paginate list endpoints
3. **Indexing**: Database indexes on frequently queried fields
4. **Caching**: Consider Redis for frequently accessed data

## Future Improvements

1. Service layer abstraction for complex business logic
2. Background task queue for async operations
3. API rate limiting
4. Comprehensive test coverage
5. API documentation with OpenAPI/Swagger
