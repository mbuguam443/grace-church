from django.contrib import admin
from .models import Song


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'key']
    list_filter = ['category']
    search_fields = ['title', 'author', 'lyrics']
