from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Course, Lesson
from .serializers import (
    CategorySerializer,
    CourseSerializer,
    CourseCreateSerializer,
    CourseUpdateSerializer,
    CourseDetailSerializer,
    LessonSerializer,
    LessonCreateSerializer,
    LessonUpdateSerializer
)


class CategoryListView(generics.ListAPIView):
    """List all categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CourseListView(generics.ListAPIView):
    """List all published courses"""
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'level', 'is_featured', 'instructor']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title', 'price']

    def get_queryset(self):
        return Course.objects.filter(is_published=True).select_related('instructor', 'category').prefetch_related('lessons')


class CourseDetailView(generics.RetrieveAPIView):
    """Get course details"""
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

    def get_queryset(self):
        return Course.objects.filter(is_published=True).select_related('instructor', 'category').prefetch_related('lessons')


class InstructorCourseListView(generics.ListCreateAPIView):
    """List and create courses for instructors"""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseCreateSerializer
        return CourseSerializer

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user).select_related('category').prefetch_related('lessons')

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)


class InstructorCourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Manage instructor's course"""
    serializer_class = CourseUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CourseUpdateSerializer
        return CourseDetailSerializer


class LessonListView(generics.ListCreateAPIView):
    """List and create lessons for a course"""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LessonCreateSerializer
        return LessonSerializer

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return Lesson.objects.filter(course_id=course_id, course__instructor=self.request.user).order_by('order_index')

    def perform_create(self, serializer):
        course_id = self.kwargs.get('course_id')
        course = Course.objects.get(id=course_id, instructor=self.request.user)
        serializer.save(course=course)


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Manage lesson details"""
    serializer_class = LessonUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Lesson.objects.filter(course__instructor=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return LessonUpdateSerializer
        return LessonSerializer


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_courses(request):
    """Get featured courses"""
    courses = Course.objects.filter(is_featured=True, is_published=True).select_related('instructor', 'category')[:6]
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def course_by_category(request, category_id):
    """Get courses by category"""
    courses = Course.objects.filter(
        category_id=category_id,
        is_published=True
    ).select_related('instructor', 'category')
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)
