from django.conf import settings
from django.db import models


class SundaySchoolCourse(models.Model):
    AGE_GROUP_CHOICES = [
        ('toddlers', 'Toddlers (2-4)'),
        ('primary', 'Primary (5-9)'),
        ('juniors', 'Juniors (10-13)'),
        ('teens', 'Teens (14-18)'),
        ('all', 'All Ages'),
    ]

    title = models.CharField(max_length=300)
    age_group = models.CharField(max_length=20, choices=AGE_GROUP_CHOICES, default='primary')
    lesson_date = models.DateField(blank=True, null=True)
    scripture = models.CharField(max_length=200, blank=True)
    memory_verse = models.CharField(max_length=300, blank=True)
    lesson = models.TextField(help_text='The teaching material for the Sunday school teacher')
    activities = models.TextField(blank=True, help_text='Suggested activities, songs or crafts for the children')
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sunday_school_courses',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-lesson_date', '-created_at']
        verbose_name_plural = 'Sunday school courses'

    def __str__(self):
        return self.title