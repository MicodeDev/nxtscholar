#!/usr/bin/env python
"""
Migration script to transition from Supabase to SQLite
This script migrates existing data from Supabase to Django's SQLite database
"""

import uuid
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nxtscholar_backend.settings')
django.setup()

def run_django_migrations():
    """Run Django migrations to create database tables"""
    print("🔄 Running Django migrations...")
    try:
        from django.core.management import call_command
        call_command('makemigrations')
        call_command('migrate')
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        sys.exit(1)

from django.contrib.auth import get_user_model
from courses.models import Category, Course, Lesson
from enrollments.models import Enrollment
from progress.models import LessonProgress
from supabase import create_client, Client
from datetime import datetime

User = get_user_model()

def connect_to_supabase():
    """Connect to Supabase"""
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_SERVICE_ROLE_KEY
    
    if not url or not key:
        print("❌ Supabase URL or service role key not configured")
        return None
    
    try:
        supabase: Client = create_client(url, key)
        return supabase
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return None

def migrate_categories(supabase):
    """Migrate categories from Supabase to SQLite"""
    print("🔄 Migrating categories...")
    
    try:
        # Get categories from Supabase
        response = supabase.table('categories').select('*').execute()
        categories_data = response.data
        
        for cat_data in categories_data:
            # Convert empty strings to None for optional fields
            description = cat_data.get('description') or None
            icon = cat_data.get('icon') or None
            
            category, created = Category.objects.get_or_create(
                id=cat_data['id'],
                defaults={
                    'name': cat_data['name'],
                    'description': description,
                    'icon': icon,
                }
            )
            
            if created:
                print(f"✅ Created category: {category.name}")
            else:
                print(f"⚠️  Category already exists: {category.name}")
        
        print(f"✅ Migrated {len(categories_data)} categories")
        return len(categories_data)
        
    except Exception as e:
        print(f"❌ Error migrating categories: {e}")
        return 0

def migrate_users(supabase):
    """Migrate users from Supabase to SQLite"""
    print("🔄 Migrating users...")
    
    try:
        # Get users from Supabase auth
        response = supabase.auth.admin.list_users()
        users_data = response.users
        
        migrated_count = 0
        
        for user_data in users_data:
            # Get profile data
            profile_response = supabase.table('profiles').select('*').eq('id', user_data.id).execute()
            profile_data = profile_response.data[0] if profile_response.data else {}
            
            # Handle email (fallback to auth email if not in profile)
            email = profile_data.get('email', user_data.email)
            if not email:
                print(f"⚠️  User {user_data.id} has no email, skipping")
                continue
                
            # Handle optional fields
            full_name = profile_data.get('full_name') or ''
            avatar_url = profile_data.get('avatar_url') or None
            role = profile_data.get('role', 'student')
            
            # Create user with hashed password (Supabase uses bcrypt)
            # Note: In a real migration, you might want to handle passwords differently
            user, created = User.objects.get_or_create(
                id=uuid.UUID(user_data.id),
                defaults={
                    'email': email,
                    'username': email,  # Django needs username
                    'full_name': full_name,
                    'avatar_url': avatar_url,
                    'role': role,
                    'password': '!',  # Set unusable password
                    'is_active': True,
                    'date_joined': datetime.fromisoformat(user_data.created_at),
                }
            )
            
            if created:
                user.set_unusable_password()  # Users will need to reset password
                user.save()
                print(f"✅ Created user: {user.email}")
                migrated_count += 1
            else:
                print(f"⚠️  User already exists: {user.email}")
        
        print(f"✅ Migrated {migrated_count} users")
        return migrated_count
        
    except Exception as e:
        print(f"❌ Error migrating users: {e}")
        return 0

def migrate_courses(supabase):
    """Migrate courses from Supabase to SQLite"""
    print("🔄 Migrating courses...")
    
    try:
        # Get courses from Supabase
        response = supabase.table('courses').select('*').execute()
        courses_data = response.data
        
        migrated_count = 0
        
        for course_data in courses_data:
            # Validate required foreign keys
            if not course_data.get('instructor_id'):
                print(f"⚠️  Course {course_data['id']} has no instructor, skipping")
                continue
                
            if not course_data.get('category_id'):
                print(f"⚠️  Course {course_data['id']} has no category, skipping")
                continue
                
            # Handle optional fields
            description = course_data.get('description') or None
            thumbnail_url = course_data.get('thumbnail_url') or None
            price = float(course_data.get('price', 0))
            
            try:
                course, created = Course.objects.get_or_create(
                    id=course_data['id'],
                    defaults={
                        'title': course_data['title'],
                        'description': description,
                        'thumbnail_url': thumbnail_url,
                        'instructor_id': course_data['instructor_id'],
                        'category_id': course_data['category_id'],
                        'price': price,
                        'is_featured': bool(course_data.get('is_featured', False)),
                        'is_published': bool(course_data.get('is_published', False)),
                        'duration_hours': int(course_data.get('duration_hours', 0)),
                        'level': course_data.get('level', 'beginner'),
                        'created_at': datetime.fromisoformat(course_data.get('created_at')) if course_data.get('created_at') else None,
                    }
                )
                
                if created:
                    print(f"✅ Created course: {course.title}")
                    migrated_count += 1
                else:
                    print(f"⚠️  Course already exists: {course.title}")
            except Exception as e:
                print(f"❌ Error creating course {course_data['id']}: {e}")
        
        print(f"✅ Migrated {migrated_count} courses")
        return migrated_count
        
    except Exception as e:
        print(f"❌ Error migrating courses: {e}")
        return 0

def migrate_lessons(supabase):
    """Migrate lessons from Supabase to SQLite"""
    print("🔄 Migrating lessons...")
    
    try:
        # Get lessons from Supabase
        response = supabase.table('lessons').select('*').execute()
        lessons_data = response.data
        
        migrated_count = 0
        
        for lesson_data in lessons_data:
            if not lesson_data.get('course_id'):
                print(f"⚠️  Lesson {lesson_data['id']} has no course, skipping")
                continue
                
            # Handle optional fields
            description = lesson_data.get('description') or None
            video_url = lesson_data.get('video_url') or None
            duration_minutes = int(lesson_data.get('duration_minutes', 0))
            order_index = int(lesson_data.get('order_index', 1))
            
            try:
                lesson, created = Lesson.objects.get_or_create(
                    id=lesson_data['id'],
                    defaults={
                        'course_id': lesson_data['course_id'],
                        'title': lesson_data['title'],
                        'description': description,
                        'video_url': video_url,
                        'duration_minutes': duration_minutes,
                        'order_index': order_index,
                        'is_free': bool(lesson_data.get('is_free', False)),
                        'created_at': datetime.fromisoformat(lesson_data.get('created_at')) if lesson_data.get('created_at') else None,
                    }
                )
                
                if created:
                    print(f"✅ Created lesson: {lesson.title}")
                    migrated_count += 1
                else:
                    print(f"⚠️  Lesson already exists: {lesson.title}")
            except Exception as e:
                print(f"❌ Error creating lesson {lesson_data['id']}: {e}")
        
        print(f"✅ Migrated {migrated_count} lessons")
        return migrated_count
        
    except Exception as e:
        print(f"❌ Error migrating lessons: {e}")
        return 0

def migrate_enrollments(supabase):
    """Migrate enrollments from Supabase to SQLite"""
    print("🔄 Migrating enrollments...")
    
    try:
        # Get enrollments from Supabase
        response = supabase.table('enrollments').select('*').execute()
        enrollments_data = response.data
        
        migrated_count = 0
        
        for enrollment_data in enrollments_data:
            if not enrollment_data.get('user_id') or not enrollment_data.get('course_id'):
                print(f"⚠️  Enrollment {enrollment_data['id']} missing user or course, skipping")
                continue
                
            # Handle optional fields
            progress_percentage = float(enrollment_data.get('progress_percentage', 0))
            completed_at = datetime.fromisoformat(enrollment_data['completed_at']) if enrollment_data.get('completed_at') else None
            
            try:
                enrollment, created = Enrollment.objects.get_or_create(
                    id=enrollment_data['id'],
                    defaults={
                        'user_id': enrollment_data['user_id'],
                        'course_id': enrollment_data['course_id'],
                        'progress_percentage': progress_percentage,
                        'completed_at': completed_at,
                        'enrolled_at': datetime.fromisoformat(enrollment_data.get('created_at')) if enrollment_data.get('created_at') else datetime.now(),
                    }
                )
                
                if created:
                    print(f"✅ Created enrollment: {enrollment.id}")
                    migrated_count += 1
                else:
                    print(f"⚠️  Enrollment already exists: {enrollment.id}")
            except Exception as e:
                print(f"❌ Error creating enrollment {enrollment_data['id']}: {e}")
        
        print(f"✅ Migrated {migrated_count} enrollments")
        return migrated_count
        
    except Exception as e:
        print(f"❌ Error migrating enrollments: {e}")
        return 0

def migrate_progress(supabase):
    """Migrate lesson progress from Supabase to SQLite"""
    print("🔄 Migrating lesson progress...")
    
    try:
        # Get lesson progress from Supabase
        response = supabase.table('lesson_progress').select('*').execute()
        progress_data = response.data
        
        migrated_count = 0
        
        for progress_item in progress_data:
            if not progress_item.get('user_id') or not progress_item.get('lesson_id'):
                print(f"⚠️  Progress record {progress_item['id']} missing user or lesson, skipping")
                continue
                
            try:
                progress, created = LessonProgress.objects.get_or_create(
                    id=progress_item['id'],
                    defaults={
                        'user_id': progress_item['user_id'],
                        'lesson_id': progress_item['lesson_id'],
                        'watch_time_seconds': int(progress_item.get('watch_time_seconds', 0)),
                        'updated_at': datetime.fromisoformat(progress_item.get('updated_at')) if progress_item.get('updated_at') else datetime.now(),
                        'is_completed': bool(progress_item.get('is_completed', False)),
                    }
                )
                
                if created:
                    print(f"✅ Created progress record: {progress.id}")
                    migrated_count += 1
                else:
                    print(f"⚠️  Progress record already exists: {progress.id}")
            except Exception as e:
                print(f"❌ Error creating progress record {progress_item['id']}: {e}")
        
        print(f"✅ Migrated {migrated_count} progress records")
        return migrated_count
        
    except Exception as e:
        print(f"❌ Error migrating progress: {e}")
        return 0

def main():
    """Main migration function"""
    print("🚀 Starting Supabase to SQLite migration...")
    
    # First ensure database tables exist
    run_django_migrations()
    
    # Then connect to Supabase and migrate data
    supabase = connect_to_supabase()
    if not supabase:
        return
    
    # Run migrations in order (respecting foreign key constraints)
    total_migrated = 0
    total_migrated += migrate_categories(supabase)
    total_migrated += migrate_users(supabase)
    total_migrated += migrate_courses(supabase)
    total_migrated += migrate_lessons(supabase)
    total_migrated += migrate_enrollments(supabase)
    total_migrated += migrate_progress(supabase)
    
    print(f"\n🎉 Migration completed! {total_migrated} records migrated to SQLite")

if __name__ == "__main__":
    main()