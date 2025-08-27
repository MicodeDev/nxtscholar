from rest_framework import serializers
from .models import Enrollment
from courses.serializers import CourseSerializer
from users.serializers import UserSerializer


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model"""
    course = CourseSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'user', 'course', 'enrolled_at', 'completed_at', 'progress_percentage']


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating enrollments"""
    class Meta:
        model = Enrollment
        fields = ['course']

    def validate_course(self, value):
        user = self.context['request'].user
        
        # Check if already enrolled
        if Enrollment.objects.filter(user=user, course=value).exists():
            raise serializers.ValidationError("You are already enrolled in this course")
        
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        return Enrollment.objects.create(user=user, **validated_data)


class EnrollmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating enrollments"""
    class Meta:
        model = Enrollment
        fields = ['progress_percentage']
