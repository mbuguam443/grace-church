from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from members.models import Member


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True, verbose_name='start time')
    end_time = models.TimeField(blank=True, null=True)
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

    def clean(self):
        super().clean()
        # On a single day the end time has to be after the start time.
        same_day = not self.end_date or self.end_date == self.date
        if self.time and self.end_time and same_day and self.end_time <= self.time:
            raise ValidationError({'end_time': 'End time must be after the start time.'})

    @property
    def time_range(self):
        """e.g. '09:00 - 12:00', or just the start when no end time is set."""
        if self.time and self.end_time:
            return '%s - %s' % (self.time.strftime('%H:%M'), self.end_time.strftime('%H:%M'))
        if self.time:
            return self.time.strftime('%H:%M')
        return ''

    @property
    def duration_minutes(self):
        if not (self.time and self.end_time):
            return None
        if self.end_date and self.end_date > self.date:
            return None  # spans days, a simple difference would be misleading
        start = self.time.hour * 60 + self.time.minute
        end = self.end_time.hour * 60 + self.end_time.minute
        return max(0, end - start)

    @property
    def duration_label(self):
        minutes = self.duration_minutes
        if not minutes:
            return ''
        hours, mins = divmod(minutes, 60)
        if hours and mins:
            return '%dh %dm' % (hours, mins)
        if hours:
            return '%dh' % hours
        return '%dm' % mins

    @property
    def days_until(self):
        """Whole days from today until the event starts; 0 means today."""
        return (self.date - date.today()).days

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
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True, related_name='event_registrations')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='event_registrations',
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ['event', 'member']

    def __str__(self):
        return f"{self.display_name} - {self.event}"

    @property
    def attendee(self):
        return self.member or self.user

    @property
    def display_name(self):
        if self.member:
            return str(self.member)
        if self.user:
            full = (self.user.get_full_name() or self.user.username).strip()
            return full or self.user.username
        return 'Unknown attendee'

    @property
    def email(self):
        if self.member:
            return self.member.email
        return (self.user.email if self.user else None) or ''

    def save(self, *args, **kwargs):
        # A registration should record either a member or a user, not both.
        if self.member_id:
            self.user = None
        super().save(*args, **kwargs)
