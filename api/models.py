import secrets

from django.conf import settings
from django.db import models


class ApiToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_tokens',
    )
    key = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} ({self.key[:8]}...)"

    @classmethod
    def create_for_user(cls, user):
        token = cls.objects.filter(user=user).first()
        if token:
            token.key = secrets.token_urlsafe(32)
            token.save(update_fields=['key'])
            return token
        return cls.objects.create(user=user, key=secrets.token_urlsafe(32))


class DeviceToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='device_tokens',
    )
    token = models.CharField(max_length=200, unique=True)
    platform = models.CharField(max_length=20, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} {self.platform}"