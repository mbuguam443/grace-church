from django.contrib import admin

from .models import BibleStudyComment, BibleStudyNote


@admin.register(BibleStudyNote)
class BibleStudyNoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'bible_verse', 'teacher', 'study_date', 'is_active']
    list_filter = ['is_active', 'study_date']
    search_fields = ['title', 'bible_verse', 'teacher', 'content']


@admin.register(BibleStudyComment)
class BibleStudyCommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'study', 'body_preview', 'attachment', 'created_at']
    list_filter = ['created_at']
    search_fields = ['body', 'study__title', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']

    def body_preview(self, obj):
        return obj.body[:80]

    body_preview.short_description = 'Comment'