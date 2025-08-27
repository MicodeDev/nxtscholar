from django.contrib import admin
from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress_percentage', 'enrolled_at', 'completed_at')
    list_filter = ('enrolled_at', 'completed_at', 'course__category')
    search_fields = ('user__email', 'user__full_name', 'course__title')
    ordering = ('-enrolled_at',)
    
    fieldsets = (
        (None, {'fields': ('user', 'course')}),
        ('Progress', {'fields': ('progress_percentage', 'completed_at')}),
        ('Timestamps', {'fields': ('enrolled_at',)}),
    )
    
    readonly_fields = ('enrolled_at',)
