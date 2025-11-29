# Lab Master API

A FastAPI-based backend for lab management, featuring user authentication (fastapi-users), PostgreSQL, and async SQLAlchemy.

## Features
- User registration & JWT authentication
- Async PostgreSQL with SQLAlchemy
- Role-based user model
- Auto table creation on startup

## Setup Instructions

### 1. Clone the repository
```
git clone https://github.com/sahilrms/lab_master.git
cd lab_master
```

### 2. Create and activate a virtual environment (optional but recommended)
```
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### 3. Install dependencies
```
uv pip install -r requirements.txt
```

### 4. Set up environment variables
- Copy `.env.example` to `.env` and edit as needed (DB credentials, secret key, etc).

### 5. Run the database (PostgreSQL)
- Make sure PostgreSQL is running and matches the `DATABASE_URL` in `.env`.

### 6. Start the API server
```
uv run uvicorn main:app --reload
```

### 7. Access API docs
- Visit http://127.0.0.1:8000/docs for Swagger UI.

---

## Notes
- First run will auto-create tables.
- For production, use proper secrets and configure CORS.
- Alembic migrations recommended for schema changes.

---

## License
MIT

