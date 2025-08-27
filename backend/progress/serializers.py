from rest_framework import serializers
from .models import LessonProgress
from courses.serializers import LessonSerializer
from users.serializers import UserSerializer


class LessonProgressSerializer(serializers.ModelSerializer):
    """Serializer for LessonProgress model"""
    lesson = LessonSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = LessonProgress
        fields = ['id', 'user', 'lesson', 'completed_at', 'watch_time_seconds']


class LessonProgressCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating lesson progress"""
    class Meta:
        model = LessonProgress
        fields = ['lesson', 'watch_time_seconds']

    def validate_lesson(self, value):
        user = self.context['request'].user
        
        # Check if user is enrolled in the course
        from enrollments.models import Enrollment
        if not Enrollment.objects.filter(user=user, course=value.course).exists():
            raise serializers.ValidationError("You must be enrolled in this course to track progress")
        
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        lesson = validated_data['lesson']
        
        # Use get_or_create to avoid duplicates
        progress, created = LessonProgress.objects.get_or_create(
            user=user,
            lesson=lesson,
            defaults={'watch_time_seconds': validated_data.get('watch_time_seconds', 0)}
        )
        
        if not created:
            # Update watch time if already exists
            progress.watch_time_seconds = validated_data.get('watch_time_seconds', progress.watch_time_seconds)
            progress.save()
        
        return progress


class LessonProgressUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating lesson progress"""
    class Meta:
        model = LessonProgress
        fields = ['watch_time_seconds']
