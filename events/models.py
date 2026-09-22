from django.db import models
from members.models import Member


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    organizer = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='organized_events')
    speaker = models.CharField(max_length=200, blank=True)
    capacity = models.PositiveIntegerField(default=0, help_text='0 for unlimited')
    registration_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} - {self.date}"

    @property
    def registrations_count(self):
        return self.registrations.count()

    @property
    def is_full(self):
        if self.capacity == 0:
            return False
        return self.registrations.count() >= self.capacity


class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='event_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ['event', 'member']

    def __str__(self):
        return f"{self.member} - {self.event}"
