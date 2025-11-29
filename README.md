# Lab Master API

A FastAPI-based backend for diagnostic lab management, featuring user authentication (fastapi-users), PostgreSQL, and async SQLAlchemy with comprehensive role-based access control.

## Features
- 🔐 User registration & JWT authentication
- 🗄️ Async PostgreSQL with SQLAlchemy
- 👥 Role-based user model (Admin, Receptionist, Lab Technician, Patient)
- ⚡ Auto table creation on startup
- 📊 Test and sample management
- 🔄 Real-time status updates

## Role-Based Functionality

### 👩‍💼 Receptionist
- **Patient Management**
  - Register new patients
  - Update patient information
  - View patient history

- **Test Management**
  - Create new test orders
  - Schedule and track tests
  - View test status and results
  - Print test reports

- **Appointments**
  - Schedule and manage appointments
  - Send appointment reminders
  - Handle walk-in patients

- **Billing**
  - Generate invoices
  - Process payments
  - Manage insurance claims

### 🔬 Lab Technician
- **Sample Processing**
  - Receive and log samples
  - Update sample status
  - Track sample location and chain of custody

- **Test Execution**
  - Perform lab tests
  - Record test results
  - Validate test quality
  - Flag abnormal results

- **Equipment Management**
  - Log equipment usage
  - Report maintenance needs
  - Perform quality control checks

- **Results Management**
  - Enter and verify test results
  - Flag critical values
  - Generate test reports
  - Send results for review

### 🏥 Admin
- **User Management**
  - Create and manage user accounts
  - Assign and modify roles
  - Monitor system usage

- **System Configuration**
  - Configure test types and panels
  - Set up reference ranges
  - Manage billing rates

- **Reporting**
  - Generate operational reports
  - View audit logs
  - Export data for analysis

### 👤 Patient
- View personal test results
- Track test status
- Access historical records
- Download reports

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip/uv package manager

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

### 7. Access API Documentation

Once the server is running, you can access the following:

- **Interactive API Docs (Swagger UI)**: http://127.0.0.1:8000/docs
- **Alternative API Docs (ReDoc)**: http://127.0.0.1:8000/redoc
- **API Root**: http://127.0.0.1:8000/

## 📝 Notes

- First run will automatically create all required database tables.
- For production deployments:
  - Use proper secrets management
  - Configure CORS appropriately
  - Set up proper logging and monitoring
  - Consider using Alembic for database migrations

## 📚 API Endpoints

### Authentication
- `POST /auth/jwt/login` - Get JWT token
- `POST /auth/register` - Register new user
- `GET /users/me` - Get current user profile

### Tests (Receptionist/Technician/Admin)
- `POST /api/v1/tests/` - Create test order
- `GET /api/v1/tests/` - List all tests
- `GET /api/v1/tests/{test_id}` - Get test details
- `PATCH /api/v1/tests/{test_id}` - Update test
- `POST /api/v1/tests/{test_id}/result` - Add test results

### Samples (Technician/Admin)
- `GET /api/v1/samples/{sample_id}` - Get sample details
- `PATCH /api/v1/samples/{sample_id}` - Update sample status

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Authentication with [FastAPI Users](https://frankie567.github.io/fastapi-users/)
- Database with [SQLAlchemy](https://www.sqlalchemy.org/) and [asyncpg](https://magicstack.github.io/asyncpg/current/)
- Project structure inspired by [FastAPI Project Structure](https://github.com/tiangolo/full-stack-fastapi-postgresql)

