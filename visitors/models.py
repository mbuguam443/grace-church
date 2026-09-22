from django.db import models
from members.models import Member


class Visitor(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('follow_up', 'Follow-up Required'),
        ('joined', 'Joined'),
        ('not_interested', 'Not Interested'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    visit_date = models.DateField()
    service_attended = models.CharField(max_length=100, blank=True)
    how_they_heard = models.CharField(max_length=200, blank=True)
    follow_up_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    assigned_to = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_visitors')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-visit_date']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.visit_date}"
