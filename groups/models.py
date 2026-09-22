from django.db import models
from members.models import Member


class Group(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    leader = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='led_groups')
    assistant_leader = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='assistant_groups')
    meeting_day = models.CharField(max_length=20, blank=True)
    meeting_time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    members = models.ManyToManyField(Member, blank=True, related_name='groups')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def members_count(self):
        return self.members.count()


class GroupAttendance(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_attendances')
    date = models.DateField()
    members = models.ManyToManyField(Member, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Group Attendances'

    def __str__(self):
        return f"{self.group} - {self.date}"
