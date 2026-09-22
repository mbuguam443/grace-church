from django.db import models
from members.models import Member
from services.models import Service


class Attendance(models.Model):
    ATTENDANCE_TYPE_CHOICES = [
        ('member', 'Member'),
        ('visitor', 'Visitor'),
        ('child', 'Child'),
    ]

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='attendances')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendances', null=True, blank=True)
    attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPE_CHOICES, default='member')
    visitor_name = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['service', 'member']
        ordering = ['-created_at']

    def __str__(self):
        if self.member:
            return f"{self.member} - {self.service}"
        return f"{self.visitor_name} - {self.service}"
