# lesson_progress/views.py (updated with correct auth)
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
import jwt
from django.contrib.auth import get_user_model
from .models import LessonProgress
from .serializers import (
    LessonProgressSerializer,
    LessonProgressCreateSerializer,
    LessonProgressUpdateSerializer
)

User = get_user_model()

class IsAuthenticatedOrSupabase(permissions.BasePermission):
    """
    Allow access if:
    - Django user is authenticated, or
    - Supabase token is valid
    """
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return True

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return False

        try:
            token_type, token = auth_header.split()
            if token_type.lower() != "bearer":
                return False

            # Use the same decoding as enrollment views
            payload = jwt.decode(
                token,
                settings.SUPABASE_PUBLIC_KEY,
                algorithms=["RS256"],
                options={"verify_aud": False}
            )

            # Create or get Django user
            user, _ = User.objects.get_or_create(
                email=payload.get("email"),
                defaults={"username": payload.get("sub")[:30]}
            )
            request.user = user
            return True

        except jwt.ExpiredSignatureError:
            print("Supabase token expired")
            return False
        except jwt.InvalidTokenError as e:
            print("Supabase auth failed:", e)
            return False
        except Exception as e:
            print("Supabase auth error:", e)
            return False


class LessonProgressListView(generics.ListCreateAPIView):
    """List and create lesson progress for the current user"""
    permission_classes = [IsAuthenticatedOrSupabase]

    def get_serializer_class(self):
        return LessonProgressCreateSerializer if self.request.method == 'POST' else LessonProgressSerializer

    def get_queryset(self):
        return LessonProgress.objects.filter(user=self.request.user).select_related('lesson', 'lesson__course')


class LessonProgressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Manage lesson progress details"""
    permission_classes = [IsAuthenticatedOrSupabase]
    lookup_field = 'id'

    def get_queryset(self):
        return LessonProgress.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        return LessonProgressUpdateSerializer if self.request.method in ['PUT', 'PATCH'] else LessonProgressSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticatedOrSupabase])
def mark_lesson_complete(request, lesson_id):
    """Mark a lesson as complete"""
    from courses.models import Lesson
    from enrollments.models import Enrollment

    try:
        lesson = Lesson.objects.get(id=lesson_id)
    except Lesson.DoesNotExist:
        return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)

    if not Enrollment.objects.filter(user=request.user, course=lesson.course).exists():
        return Response({'error': 'You must be enrolled in this course'}, status=status.HTTP_403_FORBIDDEN)

    progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'watch_time_seconds': lesson.duration_minutes * 60}
    )

    if not created:
        progress.watch_time_seconds = lesson.duration_minutes * 60
        progress.save()

    serializer = LessonProgressSerializer(progress)
    return Response({'message': 'Lesson marked as complete', 'progress': serializer.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticatedOrSupabase])
def update_watch_time(request, lesson_id):
    """Update watch time for a lesson"""
    from courses.models import Lesson
    from enrollments.models import Enrollment

    try:
        lesson = Lesson.objects.get(id=lesson_id)
    except Lesson.DoesNotExist:
        return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)

    watch_time = request.data.get('watch_time_seconds', 0)

    if not Enrollment.objects.filter(user=request.user, course=lesson.course).exists():
        return Response({'error': 'You must be enrolled in this course'}, status=status.HTTP_403_FORBIDDEN)

    progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'watch_time_seconds': watch_time}
    )

    if not created:
        progress.watch_time_seconds = watch_time
        progress.save()

    serializer = LessonProgressSerializer(progress)
    return Response({'message': 'Watch time updated', 'progress': serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrSupabase])
def course_progress(request, course_id):
    """Get progress for all lessons in a course"""
    from courses.models import Course
    from enrollments.models import Enrollment

    try:
        course = Course.objects.get(id=course_id)
        enrollment = Enrollment.objects.get(user=request.user, course=course)
    except (Course.DoesNotExist, Enrollment.DoesNotExist):
        return Response({'error': 'Course not found or you are not enrolled'}, status=status.HTTP_404_NOT_FOUND)

    lessons = course.lessons.all()
    progress_data = []

    for lesson in lessons:
        try:
            progress = LessonProgress.objects.get(user=request.user, lesson=lesson)
            is_completed = progress.watch_time_seconds >= lesson.duration_minutes * 60 * 0.8
        except LessonProgress.DoesNotExist:
            progress = None
            is_completed = False

        progress_data.append({
            'lesson_id': lesson.id,
            'lesson_title': lesson.title,
            'duration_minutes': lesson.duration_minutes,
            'is_completed': is_completed,
            'watch_time_seconds': progress.watch_time_seconds if progress else 0,
            'completed_at': progress.completed_at if progress else None
        })

    return Response({
        'course_id': course.id,
        'course_title': course.title,
        'enrollment_progress': enrollment.progress_percentage,
        'total_lessons': len(lessons),
        'completed_lessons': sum(1 for p in progress_data if p['is_completed']),
        'lessons': progress_data
    })