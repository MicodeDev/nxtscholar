from django.contrib import admin
from .models import LessonProgress


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'watch_time_seconds', 'completed_at')
    list_filter = ('completed_at', 'lesson__course__category')
    search_fields = ('user__email', 'user__full_name', 'lesson__title', 'lesson__course__title')
    ordering = ('-completed_at',)
    
    fieldsets = (
        (None, {'fields': ('user', 'lesson')}),
        ('Progress', {'fields': ('watch_time_seconds',)}),
        ('Timestamps', {'fields': ('completed_at',)}),
    )
    
    readonly_fields = ('completed_at',)
