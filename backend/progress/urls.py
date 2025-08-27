from django.urls import path
from . import views

urlpatterns = [
    path('', views.LessonProgressListView.as_view(), name='progress-list'),
    path('<uuid:id>/', views.LessonProgressDetailView.as_view(), name='progress-detail'),
    path('complete/<uuid:lesson_id>/', views.mark_lesson_complete, name='mark-lesson-complete'),
    path('watch-time/<uuid:lesson_id>/', views.update_watch_time, name='update-watch-time'),
    path('course/<uuid:course_id>/', views.course_progress, name='course-progress'),
]
