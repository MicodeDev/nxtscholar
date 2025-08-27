# accounts/models.py
from django.conf import settings
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # <-- use this instead of User
        on_delete=models.CASCADE
    )
    supabase_id = models.CharField(max_length=255, unique=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return getattr(self.user, 'username', str(self.supabase_id))
