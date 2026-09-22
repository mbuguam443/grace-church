from django.contrib import admin
from .models import BibleStudyNote


@admin.register(BibleStudyNote)
class BibleStudyNoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'bible_verse', 'teacher', 'study_date', 'is_active']
    list_filter = ['is_active', 'study_date']
    search_fields = ['title', 'bible_verse', 'teacher', 'content']
