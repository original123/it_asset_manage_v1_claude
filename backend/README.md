# IT Asset Management Backend

Flask-based REST API backend for the IT Asset Management Platform.

## Quick Start

### 1. Environment Setup

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# IMPORTANT: Update DATABASE_URL with your actual database credentials
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
export FLASK_APP=run.py
flask init-db
```

### 4. Generate Sample Data (Optional)

```bash
flask generate-data
```

### 5. Run Development Server

```bash
python run.py
# or
flask run --host=0.0.0.0 --port=5001
```

## Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | Database connection string | `mysql+pymysql://user:pass@host:3306/db` |
| `SECRET_KEY` | Yes (prod) | Flask secret key | Random 32+ char string |
| `JWT_SECRET_KEY` | Yes (prod) | JWT signing key | Random 32+ char string |
| `FLASK_ENV` | No | Environment mode | `development` or `production` |
| `CORS_ORIGINS` | No | Allowed CORS origins | `http://localhost:5173` |

## API Endpoints

- `POST /api/auth/login` - User authentication
- `GET /api/servers` - List servers
- `GET /api/containers` - List containers
- `GET /api/services` - List services
- `GET /api/gpus` - List GPUs
- `GET /api/datacenters` - List datacenters

See API documentation for full endpoint reference.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py      # Application factory
│   ├── extensions.py    # Flask extensions
│   ├── models/          # SQLAlchemy models
│   ├── routes/          # API blueprints
│   ├── schemas/         # Validation schemas (marshmallow)
│   └── utils/           # Helper functions
├── config.py            # Configuration classes
├── run.py               # Entry point
├── .env                 # Environment variables (not in git)
└── .env.example         # Environment template
```

## Security Notes

- **Never commit `.env` file** - it contains sensitive credentials
- Database credentials are loaded from environment variables only
- Default SQLite fallback is for development only
- Change `SECRET_KEY` and `JWT_SECRET_KEY` in production
