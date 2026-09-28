from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('pastor', 'Pastor'),
        ('secretary', 'Secretary'),
        ('finance_officer', 'Finance Officer'),
        ('ministry_leader', 'Ministry Leader'),
        ('group_leader', 'Group Leader'),
        ('media', 'Media'),
        ('usher', 'Usher'),
        ('worship_team', 'Praise & Worship Team'),
        ('member', 'Member'),
    ]

    AGE_GROUP_CHOICES = [
        ('', 'Not set'),
        ('toddlers', 'Toddlers (2-4)'),
        ('primary', 'Primary (5-9)'),
        ('juniors', 'Juniors (10-13)'),
        ('teens', 'Teens (14-18)'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    age_group = models.CharField(
        max_length=20, choices=AGE_GROUP_CHOICES, blank=True, default='',
        help_text='Used to target Sunday School classes by age group.',
    )
    phone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='users/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_admin_user(self):
        return self.role in ['super_admin', 'admin']

    @property
    def is_leader(self):
        return self.role in ['super_admin', 'admin', 'pastor', 'ministry_leader', 'group_leader']

    @property
    def is_finance(self):
        return self.role in ['super_admin', 'admin', 'finance_officer']

    @property
    def is_pastoral(self):
        return self.role in ['super_admin', 'admin', 'pastor']

    @property
    def is_worship_team(self):
        return self.role in ['super_admin', 'admin', 'pastor', 'ministry_leader', 'worship_team']

    @property
    def can_manage_content(self):
        return self.role in ['super_admin', 'admin', 'pastor', 'secretary']
