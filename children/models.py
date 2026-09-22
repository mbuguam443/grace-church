from django.db import models
from members.models import Member


class Child(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    parent = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    school_class = models.CharField(max_length=50, blank=True)
    teacher = models.CharField(max_length=100, blank=True)
    allergies = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='children/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Children'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class ChildAttendance(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    checked_in = models.BooleanField(default=False)
    checked_out = models.BooleanField(default=False)
    checkin_time = models.TimeField(blank=True, null=True)
    checkout_time = models.TimeField(blank=True, null=True)
    checked_in_by = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='child_checkins')
    checked_out_by = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='child_checkouts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['child', 'date']

    def __str__(self):
        return f"{self.child} - {self.date}"
