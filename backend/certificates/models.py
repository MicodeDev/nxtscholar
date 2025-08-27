from django.db import models
from django.contrib.auth import get_user_model
from courses.models import Course
import uuid

User = get_user_model()


class Certificate(models.Model):
    """Certificate model for completed courses"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    certificate_url = models.URLField(blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

    class Meta:
        db_table = 'certificates'
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.email} - {self.course.title} Certificate"
