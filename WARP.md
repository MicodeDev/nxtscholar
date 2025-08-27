# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

NXTSCHOLAR is an e-learning platform designed for African students, built with a Django REST API backend and Next.js frontend. The platform provides course management, user authentication, progress tracking, and enrollment functionality.

## Development Commands

### Backend (Django) - `/backend` directory

**Setup and Environment:**
```bash
# Navigate to backend directory
cd backend

# Run automated setup (recommended)
python setup.py

# Manual setup
python -m venv venv
# Windows: venv\Scripts\activate
# Unix/Mac: source venv/bin/activate
pip install -r requirements.txt
```

**Database Operations:**
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Reset database (if needed)
# Delete db.sqlite3 and migration files, then re-run migrations
```

**Development Server:**
```bash
# Start Django development server
python manage.py runserver

# Run on specific port
python manage.py runserver 8000
```

**Testing:**
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test courses
python manage.py test enrollments
```

**Database Debugging:**
```bash
# Check database connection
python manage.py check --database default

# Open Django shell
python manage.py shell

# Collect static files (for production)
python manage.py collectstatic --noinput
```

### Frontend (Next.js) - `/NxtSCholar` directory

**Development:**
```bash
# Navigate to frontend directory
cd NxtSCholar

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint
```

## Architecture Overview

### Backend Architecture (Django)

**Core Structure:**
- **Django REST Framework** with JWT authentication
- **SQLite** database (production can use PostgreSQL)
- **Modular app structure** with clear separation of concerns

**Key Django Apps:**
- `users/` - Custom user model with email authentication
- `courses/` - Course, Category, and Lesson models with instructor management
- `enrollments/` - Course enrollment tracking
- `progress/` - Lesson progress and completion tracking
- `payments/` - Payment processing (future feature)
- `certificates/` - Certificate generation (future feature)

**Authentication Flow:**
- JWT-based authentication with SimpleJWT
- Custom User model using email as username
- Role-based access (student, instructor)

**API Endpoints Structure:**
```
/api/auth/           # User authentication and profile
/api/courses/        # Course management and browsing
/api/enrollments/    # Course enrollment operations
/api/progress/       # Learning progress tracking
```

### Frontend Architecture (Next.js)

**Technology Stack:**
- **Next.js 15.2.4** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling with custom components
- **Radix UI** for accessible UI components
- **React Hook Form** with Zod validation

**Key Patterns:**
- **Component-based architecture** in `/components`
- **Page routing** in `/app` directory
- **API client abstraction** in `/lib/api/client.ts`
- **Type definitions** for Django API responses

### Data Flow Integration

**Frontend → Backend Communication:**
- REST API calls through TypeScript API client
- JWT tokens passed in Authorization headers
- Type-safe interfaces matching Django serializers

**Key Data Models:**
- `User` - Custom user model with email authentication
- `Course` - Course content with instructor and category relationships  
- `Lesson` - Video lessons with ordering and duration
- `Enrollment` - User course enrollments with progress tracking
- `Category` - Course categorization system

## Development Workflow

### Adding New Features

**Backend (Django):**
1. Create models in appropriate app's `models.py`
2. Create serializers in `serializers.py`
3. Create views in `views.py` (prefer class-based views)
4. Add URL patterns in app's `urls.py`
5. Run `python manage.py makemigrations && python manage.py migrate`

**Frontend (Next.js):**
1. Add TypeScript interfaces matching Django serializers
2. Update API client in `lib/api/client.ts`
3. Create components in `/components`
4. Add pages in `/app` directory

### Database Schema

**Core Tables:**
- `users_user` - Custom user model
- `categories` - Course categories
- `courses` - Course information with instructor FK
- `lessons` - Course lessons with ordering
- `enrollments` - User course enrollments
- `lesson_progress` - Individual lesson completion tracking

### Common Issues & Solutions

**Backend:**
- SQLite file locking: The app includes WAL mode configuration for better concurrency
- Migration conflicts: Use `python setup.py` for automated reset if needed
- Database connection issues: Check the test.py file for DNS debugging utilities

**Frontend:**
- API connection: Default API URL is `http://127.0.0.1:8000/api`
- Environment variables: Set `NEXT_PUBLIC_API_URL` for different API endpoints
- Build issues: Ensure all dependencies are installed with `npm install`

## Testing

**Backend Testing:**
- Django's built-in test framework
- Tests located in each app's `tests.py` (to be created)
- Test database automatically created/destroyed

**Frontend Testing:**
- No testing framework currently configured
- Consider adding Jest/React Testing Library for comprehensive testing

## Deployment Considerations

**Backend:**
- SQLite suitable for development, PostgreSQL recommended for production
- Environment variables should be configured in `.env`
- Static files collection needed for production
- CORS settings configured for localhost:3000

**Frontend:**
- Standard Next.js build process
- Tailwind CSS compilation included
- API URL configuration needed for production backend

## Code Style & Patterns

**Backend (Django):**
- Follow Django REST Framework conventions
- Use class-based views for consistency
- UUID primary keys for all models
- Proper model relationships with related_name

**Frontend (Next.js):**
- TypeScript strict mode enabled
- Tailwind CSS for styling
- Component composition pattern
- API client abstraction pattern

