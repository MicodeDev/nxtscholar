from django.contrib import admin
from .models import Category, Course, Lesson


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    ordering = ('order_index',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'price', 'is_published', 'is_featured', 'created_at')
    list_filter = ('is_published', 'is_featured', 'level', 'category', 'created_at')
    search_fields = ('title', 'description', 'instructor__email', 'instructor__full_name')
    ordering = ('-created_at',)
    inlines = [LessonInline]
    
    fieldsets = (
        (None, {'fields': ('title', 'description', 'instructor')}),
        ('Course Details', {'fields': ('category', 'price', 'level', 'duration_hours')}),
        ('Status', {'fields': ('is_published', 'is_featured')}),
        ('Media', {'fields': ('thumbnail_url',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order_index', 'duration_minutes', 'is_free', 'created_at')
    list_filter = ('is_free', 'course__category', 'created_at')
    search_fields = ('title', 'description', 'course__title')
    ordering = ('course', 'order_index')
    
    fieldsets = (
        (None, {'fields': ('course', 'title', 'description')}),
        ('Lesson Details', {'fields': ('order_index', 'duration_minutes', 'is_free')}),
        ('Media', {'fields': ('video_url',)}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
    
    readonly_fields = ('created_at',)
