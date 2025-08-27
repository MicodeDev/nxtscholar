from django.db import models
from django.contrib.auth import get_user_model
from courses.models import Course
import uuid

User = get_user_model()


class Enrollment(models.Model):
    """Course enrollment model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.IntegerField(default=0)

    class Meta:
        db_table = 'enrollments'
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"

    def update_progress(self):
        """Update progress percentage based on completed lessons"""
        from progress.models import LessonProgress
        
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            self.progress_percentage = 0
        else:
            completed_lessons = LessonProgress.objects.filter(
                user=self.user,
                lesson__course=self.course
            ).count()
            self.progress_percentage = int((completed_lessons / total_lessons) * 100)
        
        # Mark as completed if 100%
        if self.progress_percentage == 100 and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
        
        self.save()
