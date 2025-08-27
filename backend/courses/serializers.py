from rest_framework import serializers
from .models import Category, Course, Lesson
from users.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'created_at']


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model"""
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'video_url', 'duration_minutes', 'order_index', 'is_free', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model"""
    instructor = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)
    total_lessons = serializers.ReadOnlyField()
    total_duration_minutes = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'thumbnail_url', 'instructor', 'category',
            'price', 'is_featured', 'is_published', 'duration_hours', 'level',
            'created_at', 'updated_at', 'lessons', 'total_lessons', 'total_duration_minutes'
        ]


class CourseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating courses"""
    class Meta:
        model = Course
        fields = ['title', 'description', 'thumbnail_url', 'category', 'price', 'level', 'duration_hours']


class CourseUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating courses"""
    class Meta:
        model = Course
        fields = ['title', 'description', 'thumbnail_url', 'category', 'price', 'level', 'duration_hours', 'is_published']


class LessonCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating lessons"""
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'video_url', 'duration_minutes', 'order_index', 'is_free']


class LessonUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating lessons"""
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'video_url', 'duration_minutes', 'order_index', 'is_free']


class CourseDetailSerializer(CourseSerializer):
    """Detailed course serializer with full lesson information"""
    lessons = LessonSerializer(many=True, read_only=True)
