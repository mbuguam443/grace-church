from django.db import models


class Sermon(models.Model):
    CATEGORY_CHOICES = [
        ('sunday', 'Sunday Service'),
        ('midweek', 'Midweek'),
        ('evangelism', 'Evangelism'),
        ('teaching', 'Teaching'),
        ('devotion', 'Devotion'),
        ('youth', 'Youth'),
        ('special', 'Special Service'),
    ]

    title = models.CharField(max_length=300)
    speaker = models.CharField(max_length=200, help_text='Who gave the sermon')
    date = models.DateField()
    bible_verse = models.CharField(max_length=200, blank=True)
    series = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, blank=True)
    description = models.TextField(blank=True)
    sermon_notes = models.TextField(blank=True)
    youtube_url = models.URLField(blank=True)
    audio_file = models.FileField(upload_to='sermons/audio/', blank=True, null=True)
    video_file = models.FileField(upload_to='sermons/video/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='sermons/pdf/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - {self.speaker}"
