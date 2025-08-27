# NXTSCHOLAR Django Backend

This is the Django REST API backend for the NXTSCHOLAR e-learning platform. It provides secure API endpoints for course management, user authentication, progress tracking, and more.

## Architecture Overview

The backend follows the architecture described in the main project:

- **Django + DRF**: Handles all business logic, authentication, and API endpoints
- **Supabase PostgreSQL**: Database for all structured data
- **Supabase Storage**: File storage for videos, PDFs, and images
- **JWT Authentication**: Secure token-based authentication

## Features

### Core Functionality
- ✅ User authentication and authorization
- ✅ Course management (CRUD operations)
- ✅ Lesson management with ordering
- ✅ Course enrollment system
- ✅ Progress tracking for lessons
- ✅ Category management
- ✅ Instructor role management

### API Endpoints

#### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/me/` - Get current user
- `PUT /api/auth/profile/` - Update user profile
- `POST /api/auth/change-password/` - Change password

#### JWT Tokens
- `POST /api/token/` - Get JWT access token
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/token/verify/` - Verify JWT token

#### Courses
- `GET /api/courses/` - List all published courses
- `GET /api/courses/featured/` - Get featured courses
- `GET /api/courses/{id}/` - Get course details
- `GET /api/courses/categories/` - List all categories
- `GET /api/courses/category/{category_id}/` - Get courses by category

#### Instructor Course Management
- `GET /api/courses/instructor/` - List instructor's courses
- `POST /api/courses/instructor/` - Create new course
- `PUT /api/courses/instructor/{id}/` - Update course
- `DELETE /api/courses/instructor/{id}/` - Delete course
- `GET /api/courses/instructor/{course_id}/lessons/` - List course lessons
- `POST /api/courses/instructor/{course_id}/lessons/` - Add lesson to course

#### Enrollments
- `GET /api/enrollments/` - List user enrollments
- `POST /api/enrollments/enroll/{course_id}/` - Enroll in course
- `DELETE /api/enrollments/unenroll/{course_id}/` - Unenroll from course
- `GET /api/enrollments/check/{course_id}/` - Check enrollment status

#### Progress Tracking
- `GET /api/progress/` - List user's lesson progress
- `POST /api/progress/complete/{lesson_id}/` - Mark lesson as complete
- `POST /api/progress/watch-time/{lesson_id}/` - Update watch time
- `GET /api/progress/course/{course_id}/` - Get course progress

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database (Supabase)
- Redis (for Celery tasks)

### Quick Setup

1. **Clone the repository and navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Manual setup (if needed)**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Unix/Mac:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Copy environment file
   cp env.example .env
   
   # Update .env with your configuration
   # Run migrations
   python manage.py makemigrations
   python manage.py migrate
   
   # Create superuser
   python manage.py createsuperuser
   
   # Collect static files
   python manage.py collectstatic --noinput
   ```

### Environment Configuration

Update the `.env` file with your actual configuration:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings (Supabase PostgreSQL)
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-database-password
DB_HOST=db.khyqmssuchivbrufloxs.supabase.co
DB_PORT=5432

# Supabase Settings
SUPABASE_URL=https://khyqmssuchivbrufloxs.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Storage Settings (Supabase Storage)
AWS_ACCESS_KEY_ID=your-supabase-storage-access-key
AWS_SECRET_ACCESS_KEY=your-supabase-storage-secret-key
AWS_STORAGE_BUCKET_NAME=your-storage-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Redis Settings (for Celery)
REDIS_URL=redis://localhost:6379/0

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
```

### Running the Server

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix/Mac

# Run development server
python manage.py runserver

# Run with specific port
python manage.py runserver 8000
```

## Database Schema

The Django models map to the existing Supabase database schema:

- `users.User` → `profiles` table
- `courses.Category` → `categories` table
- `courses.Course` → `courses` table
- `courses.Lesson` → `lessons` table
- `enrollments.Enrollment` → `enrollments` table
- `progress.LessonProgress` → `lesson_progress` table

## API Documentation

### Authentication

All API endpoints (except public ones) require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Example API Calls

#### Register a new user
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "full_name": "John Doe",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }'
```

#### Login and get JWT token
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

#### Get courses (public endpoint)
```bash
curl -X GET http://localhost:8000/api/courses/
```

#### Enroll in a course (requires authentication)
```bash
curl -X POST http://localhost:8000/api/enrollments/enroll/{course_id}/ \
  -H "Authorization: Bearer <your-jwt-token>"
```

## Development

### Project Structure
```
backend/
├── nxtscholar_backend/     # Main Django project
│   ├── settings.py         # Django settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
├── users/                 # User management app
├── courses/               # Course management app
├── enrollments/           # Enrollment management app
├── progress/              # Progress tracking app
├── payments/              # Payment processing app
├── certificates/          # Certificate generation app
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── setup.py             # Setup script
```

### Adding New Features

1. **Create new Django app** (if needed):
   ```bash
   python manage.py startapp new_app
   ```

2. **Add to INSTALLED_APPS** in `settings.py`

3. **Create models** in `new_app/models.py`

4. **Create serializers** in `new_app/serializers.py`

5. **Create views** in `new_app/views.py`

6. **Add URL patterns** in `new_app/urls.py`

7. **Include in main URLs** in `nxtscholar_backend/urls.py`

8. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test courses
```

## Deployment

### Production Settings

1. Set `DEBUG=False` in production
2. Use environment variables for sensitive data
3. Configure proper database settings
4. Set up static file serving
5. Configure HTTPS
6. Set up proper logging

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "nxtscholar_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
