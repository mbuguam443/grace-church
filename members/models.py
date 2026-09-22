from django.db import models
from django.conf import settings


class Family(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Families'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def members_count(self):
        return self.members.count()


class Member(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('visitor', 'Visitor'),
        ('transferred', 'Transferred'),
        ('deceased', 'Deceased'),
    ]
    MEMBERSHIP_TYPE_CHOICES = [
        ('full', 'Full Member'),
        ('associate', 'Associate'),
        ('adherent', 'Adherent'),
    ]
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ]

    member_number = models.CharField(max_length=20, unique=True, blank=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')])
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to='members/', blank=True, null=True)
    date_joined = models.DateField(blank=True, null=True)
    membership_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_TYPE_CHOICES, default='full')
    baptism_status = models.BooleanField(default=False)
    baptism_date = models.DateField(blank=True, null=True)
    salvation_date = models.DateField(blank=True, null=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, default='single')
    occupation = models.CharField(max_length=100, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    family = models.ForeignKey(Family, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='member_profile')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.member_number})"

    def save(self, *args, **kwargs):
        if not self.member_number:
            last = Member.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.member_number = f"GC-{num:05d}"
        super().save(*args, **kwargs)
