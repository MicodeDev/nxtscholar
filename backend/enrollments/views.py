# enrollments/views.py (updated with custom auth)
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
import jwt
from django.contrib.auth import get_user_model
from .models import Enrollment
from .serializers import (
    EnrollmentSerializer,
    EnrollmentCreateSerializer,
    EnrollmentUpdateSerializer
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

            payload = jwt.decode(
                token,
                settings.SUPABASE_PUBLIC_KEY,
                algorithms=["RS256"],
                options={"verify_aud": False}
            )

            user, _ = User.objects.get_or_create(
                email=payload.get("email"),
                defaults={"username": payload.get("sub")[:30]}
            )
            request.user = user
            return True

        except Exception as e:
            print("Supabase auth failed:", e)
            return False


class EnrollmentListView(generics.ListCreateAPIView):
    """List all enrollments for the current user or create a new one."""
    permission_classes = [IsAuthenticatedOrSupabase]

    def get_serializer_class(self):
        return EnrollmentCreateSerializer if self.request.method == 'POST' else EnrollmentSerializer

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)\
            .select_related('course', 'course__instructor', 'course__category')


class EnrollmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a user's enrollment."""
    permission_classes = [IsAuthenticatedOrSupabase]
    lookup_field = 'id'

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        return EnrollmentUpdateSerializer if self.request.method in ['PUT', 'PATCH'] else EnrollmentSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticatedOrSupabase])
def enroll_in_course(request, course_id):
    """Enroll the current user in a specific course."""
    from courses.models import Course

    try:
        course = Course.objects.get(id=course_id, is_published=True)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found or not published'}, status=status.HTTP_404_NOT_FOUND)

    if Enrollment.objects.filter(user=request.user, course=course).exists():
        return Response({'error': 'You are already enrolled in this course'}, status=status.HTTP_400_BAD_REQUEST)

    enrollment = Enrollment.objects.create(user=request.user, course=course)
    serializer = EnrollmentSerializer(enrollment)
    return Response({'message': 'Successfully enrolled in course', 'enrollment': serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticatedOrSupabase])
def unenroll_from_course(request, course_id):
    """Unenroll the current user from a course."""
    try:
        enrollment = Enrollment.objects.get(user=request.user, course_id=course_id)
        enrollment.delete()
        return Response({'message': 'Successfully unenrolled from course'}, status=status.HTTP_200_OK)
    except Enrollment.DoesNotExist:
        return Response({'error': 'Enrollment not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrSupabase])
def check_enrollment(request, course_id):
    """Check if the current user is enrolled in a specific course."""
    is_enrolled = Enrollment.objects.filter(user=request.user, course_id=course_id).exists()
    return Response({'is_enrolled': is_enrolled})
