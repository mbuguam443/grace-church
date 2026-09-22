from django.db import models
from members.models import Member


class Ministry(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    leader = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='led_ministries')
    members = models.ManyToManyField(Member, blank=True, related_name='ministries')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Ministries'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def members_count(self):
        return self.members.count()
