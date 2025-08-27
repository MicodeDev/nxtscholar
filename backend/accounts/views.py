# accounts/views.py
import requests
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile

User = get_user_model()  # <- Use your custom user model

# accounts/views.py
@api_view(["POST"])
@permission_classes([AllowAny])
def sync_user(request):
    supabase_id = request.data.get("id")
    email = request.data.get("email")
    metadata = request.data.get("user_metadata", {})

    if not supabase_id or not email:
        return Response({"error": "Missing Supabase user data"}, status=400)

    # Use email instead of username
    user, created = User.objects.get_or_create(
        email=email,
        defaults={"full_name": metadata.get("name", ""), "is_active": True}
    )

    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={"supabase_id": supabase_id, "metadata": metadata}
    )

    refresh = RefreshToken.for_user(user)
    django_token = str(refresh.access_token)

    return Response({
        "created": created,
        "user_id": user.id,
        "email": user.email,
        "django_token": django_token
    })
