from django.urls import path
from . import views

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    
    # Public course endpoints
    path('', views.CourseListView.as_view(), name='course-list'),
    path('featured/', views.featured_courses, name='featured-courses'),
    path('category/<uuid:category_id>/', views.course_by_category, name='course-by-category'),
    path('<uuid:id>/', views.CourseDetailView.as_view(), name='course-detail'),
    
    # Instructor course management
    path('instructor/', views.InstructorCourseListView.as_view(), name='instructor-course-list'),
    path('instructor/<uuid:id>/', views.InstructorCourseDetailView.as_view(), name='instructor-course-detail'),
    
    # Lesson management
    path('instructor/<uuid:course_id>/lessons/', views.LessonListView.as_view(), name='lesson-list'),
    path('instructor/lessons/<uuid:id>/', views.LessonDetailView.as_view(), name='lesson-detail'),
]
