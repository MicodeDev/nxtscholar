from django.db import models
from django.contrib.auth import get_user_model
from courses.models import Lesson
import uuid

User = get_user_model()


class LessonProgress(models.Model):
    """Lesson progress tracking model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    completed_at = models.DateTimeField(auto_now_add=True)
    watch_time_seconds = models.IntegerField(default=0)

    class Meta:
        db_table = 'lesson_progress'
        unique_together = ['user', 'lesson']

    def __str__(self):
        return f"{self.user.email} - {self.lesson.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update enrollment progress when lesson progress is saved
        self.update_enrollment_progress()

    def update_enrollment_progress(self):
        """Update the enrollment progress for this lesson's course"""
        from enrollments.models import Enrollment
        
        try:
            enrollment = Enrollment.objects.get(
                user=self.user,
                course=self.lesson.course
            )
            enrollment.update_progress()
        except Enrollment.DoesNotExist:
            pass
