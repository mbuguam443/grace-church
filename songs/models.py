from django.db import models


class Song(models.Model):
    CATEGORY_CHOICES = [
        ('praise', 'Praise'),
        ('worship', 'Worship'),
        ('hymn', 'Hymn'),
        ('gospel', 'Gospel'),
        ('chorus', 'Chorus'),
        ('contemporary', 'Contemporary'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='praise')
    lyrics = models.TextField()
    author = models.CharField(max_length=200, blank=True)
    scripture = models.CharField(max_length=200, blank=True)
    key = models.CharField(max_length=10, blank=True)
    tempo = models.CharField(max_length=20, blank=True)
    youtube_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
