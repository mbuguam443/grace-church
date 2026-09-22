from django.contrib import admin
from .models import SundaySchoolCourse


@admin.register(SundaySchoolCourse)
class SundaySchoolCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'age_group', 'lesson_date', 'is_active', 'posted_by', 'created_at')
    list_filter = ('age_group', 'is_active', 'lesson_date')
    search_fields = ('title', 'scripture', 'lesson')