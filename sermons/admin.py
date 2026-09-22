from django.contrib import admin
from .models import Sermon


@admin.register(Sermon)
class SermonAdmin(admin.ModelAdmin):
    list_display = ['title', 'speaker', 'date', 'category']
    list_filter = ['category', 'date']
    search_fields = ['title', 'speaker', 'bible_verse', 'description']
