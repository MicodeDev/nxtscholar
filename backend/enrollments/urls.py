from django.urls import path
from . import views

urlpatterns = [
    path('', views.EnrollmentListView.as_view(), name='enrollment-list'),
    path('<uuid:id>/', views.EnrollmentDetailView.as_view(), name='enrollment-detail'),
    path('enroll/<uuid:course_id>/', views.enroll_in_course, name='enroll-in-course'),
    path('unenroll/<uuid:course_id>/', views.unenroll_from_course, name='unenroll-from-course'),
    path('check/<uuid:course_id>/', views.check_enrollment, name='check-enrollment'),
]