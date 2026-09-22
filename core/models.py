from django.db import models

from accounts.models import User
from .modules import MODULES


class RoleModulePermission(models.Model):
    role = models.CharField(max_length=20, choices=User.ROLE_CHOICES)
    module = models.CharField(max_length=50, choices=MODULES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('role', 'module')
        verbose_name_plural = 'Role module permissions'

    def __str__(self):
        return f"{self.get_role_display()} -> {self.get_module_display()}"

    @classmethod
    def allowed_modules_for(cls, role):
        perms = cls.objects.filter(role=role).values_list('module', flat=True)
        if not perms.exists():
            return None
        return set(perms)


class ChurchSetting(models.Model):
    church_name = models.CharField(max_length=200, default='Grace Church Munyaka')
    short_name = models.CharField(max_length=20, default='GC')
    logo = models.ImageField(upload_to='church/', blank=True, null=True)
    favicon = models.ImageField(upload_to='church/', blank=True, null=True)
    hero_image = models.ImageField(upload_to='church/', blank=True, null=True, help_text='Homepage hero background (1920x1080 recommended)')
    events_image = models.ImageField(upload_to='church/', blank=True, null=True, help_text='Events section image')
    sermons_image = models.ImageField(upload_to='church/', blank=True, null=True, help_text='Sermons section image')
    cta_image = models.ImageField(upload_to='church/', blank=True, null=True, help_text='Call to action section image')
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    currency = models.CharField(max_length=10, default='KES')
    timezone = models.CharField(max_length=50, default='Africa/Nairobi')
    primary_color = models.CharField(max_length=7, default='#A8704A')
    secondary_color = models.CharField(max_length=7, default='#4E3A2C')
    accent_color = models.CharField(max_length=7, default='#B5651D')
    gold_color = models.CharField(max_length=7, default='#C9A24B')
    service_times = models.TextField(blank=True, help_text='One per line')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Church Setting'
        verbose_name_plural = 'Church Settings'

    def __str__(self):
        return self.church_name

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Notification(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    kind = models.CharField(max_length=40, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user}"
