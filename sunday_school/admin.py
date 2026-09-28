from django.contrib import admin
from .models import CourseComment, CourseEnrollment, SundaySchoolCourse


@admin.register(SundaySchoolCourse)
class SundaySchoolCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'age_group', 'lesson_date', 'enable_registration', 'is_active', 'posted_by', 'created_at')
    list_filter = ('age_group', 'is_active', 'enable_registration', 'lesson_date')
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


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'course', 'status', 'joined_at', 'approved_at']
    list_filter = ['status', 'joined_at', 'course']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'course__title']
    readonly_fields = ['joined_at']

    def student_name(self, obj):
        return obj.student_name

    student_name.short_description = 'Student'