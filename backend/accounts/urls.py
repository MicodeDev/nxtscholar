# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.sync_user, name='sync_user'),
]
