from django.contrib import admin

from .models import BibleStudyComment, BibleStudyEnrollment, BibleStudyNote


@admin.register(BibleStudyNote)
class BibleStudyNoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'bible_verse', 'teacher', 'study_date', 'enable_registration', 'is_active']
    list_filter = ['is_active', 'study_date', 'enable_registration']
    search_fields = ['title', 'bible_verse', 'teacher__first_name', 'teacher__last_name', 'content']


@admin.register(BibleStudyComment)
class BibleStudyCommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'study', 'body_preview', 'attachment', 'created_at']
    list_filter = ['created_at']
    search_fields = ['body', 'study__title', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']

    def body_preview(self, obj):
        return obj.body[:80]

    body_preview.short_description = 'Comment'


@admin.register(BibleStudyEnrollment)
class BibleStudyEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'study', 'status', 'joined_at', 'approved_at']
    list_filter = ['status', 'joined_at', 'study']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'study__title']
    readonly_fields = ['joined_at']

    def student_name(self, obj):
        return obj.student_name

    student_name.short_description = 'Student'