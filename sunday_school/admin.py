from django.contrib import admin
from .models import CourseComment, SundaySchoolCourse


@admin.register(SundaySchoolCourse)
class SundaySchoolCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'age_group', 'lesson_date', 'is_active', 'posted_by', 'created_at')
    list_filter = ('age_group', 'is_active', 'lesson_date')
    search_fields = ('title', 'scripture', 'lesson')


@admin.register(CourseComment)
class CourseCommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'body_preview', 'attachment', 'created_at']
    list_filter = ['created_at']
    search_fields = ['body', 'course__title', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']

    def body_preview(self, obj):
        return obj.body[:80]

    body_preview.short_description = 'Comment'