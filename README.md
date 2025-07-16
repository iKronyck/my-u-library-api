# My U Library API

A complete REST API for managing a university library, developed with Django and Django REST Framework.

## 🛠️ Technologies Used

### Backend

- **Django 5.2.4** - Python web framework
- **Django REST Framework** - REST API framework
- **Django CORS Headers** - CORS handling
- **Django REST Framework Simple JWT** - JWT authentication
- **PostgreSQL** - Database
- **Gunicorn** - WSGI server for production
- **python-decouple** - Environment variables management

### Deployment

- **Railway** - Deployment platform
- **Vercel** - Frontend (separate)

## 📁 Project Structure

```
my-u-library-backend/
├── config/                     # Main Django configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py            # Main configuration
│   ├── urls.py                # Main URLs
│   ├── wsgi.py
│   └── settings/
│       ├── __init__.py
│       └── env.py             # Environment variables configuration
├── library/                    # Main application
│   ├── __init__.py
│   ├── admin.py               # Django admin configuration
│   ├── apps.py
│   ├── models.py              # Data models
│   ├── serializers.py         # API serializers
│   ├── urls.py                # Application URLs
│   ├── utils.py               # Utilities (email sending)
│   ├── views.py               # API views
│   ├── tests.py
│   └── migrations/            # Database migrations
│       ├── __init__.py
│       ├── 0001_initial.py
│       ├── 0002_bookloan.py
│       └── 0003_alter_bookloan_status.py
├── manage.py                  # Django management script
├── requirements.txt           # Project dependencies
├── Procfile                  # Railway configuration
└── README.md                 # This file
```

## 🚀 How to Run the Project

### Prerequisites

- Python 3.8+
- PostgreSQL
- pip

### 1. Clone the repository

```bash
git clone <repository-url>
cd my-u-library-backend
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database Settings
DB_NAME=library_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@library.com

# Frontend URL
FRONTEND_URL=http://localhost:3000

# CORS Settings
CORS_ALLOWED_ORIGINS=["http://localhost:3000"]
```

### 5. Configure database

```bash
# Create PostgreSQL database
createdb library_db

# Run migrations
python manage.py migrate
```

### 6. Create superuser (optional)

```bash
python manage.py createsuperuser
```

### 7. Run development server

```bash
python manage.py runserver
```

The API will be available at: `http://localhost:8000`

## 📚 API Endpoints

### Authentication

- `POST /api/register/` - Register user
- `GET /api/magic-login/?token=<token>` - Login with magic link
- `POST /api/resend-magic-link/` - Resend magic link

### Books

- `GET /api/books/` - List books
- `POST /api/books/` - Create book
- `GET /api/books/{id}/` - Get specific book
- `PUT /api/books/{id}/` - Update book
- `DELETE /api/books/{id}/` - Delete book

### Users

- `GET /api/users/` - List users
- `GET /api/users/{id}/` - Get specific user

### Loans

- `GET /api/loans/` - List loans
- `POST /api/loan-book/` - Loan book
- `POST /api/loans/{id}/return/` - Return book
- `POST /api/loans/{id}/mark-lost/` - Mark book as lost
- `GET /api/my-loans/` - My loans

### Dashboard and Statistics

- `GET /api/dashboard-stats/` - Dashboard statistics
- `GET /api/activity-feed/` - Activity feed

## 🔐 Authentication

### Magic Link

1. Register with email
2. Receive magic link by email
3. Click on the link to get JWT token
4. Use token in header: `Authorization: Bearer <token>`

### Token Duration

- **Magic Link**: 30 days
- **Access Token**: 30 days
- **Refresh Token**: 30 days

## 👥 User Roles

- **Student**: Can loan books and view their loans
- **Librarian**: Can manage books, loans and users

## 📧 Email Configuration

The system uses Gmail SMTP to send magic links. Configure:

- EMAIL_HOST_USER: Your Gmail email
- EMAIL_HOST_PASSWORD: Gmail app password

## 🧪 Testing

```bash
python manage.py test
```

## 📝 Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```
