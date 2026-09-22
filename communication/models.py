from django.db import models


class Announcement(models.Model):
    TARGET_CHOICES = [
        ('everyone', 'Everyone'),
        ('members', 'Members'),
        ('youth', 'Youth'),
        ('men', 'Men'),
        ('women', 'Women'),
        ('ministry', 'Ministry'),
        ('group', 'Group'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    target_audience = models.CharField(max_length=20, choices=TARGET_CHOICES, default='everyone')
    publish_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
