from django.db import models
from django.utils import timezone


class FundedPerson(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Food & Family Support'),
        ('scholarship', 'School Fees & Scholarships'),
        ('medical', 'Medical Support'),
        ('other', 'Other Support'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    record_number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='food')
    date_helped = models.DateField(default=timezone.localdate, verbose_name='Date Admitted')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    date_of_birth = models.DateField(
        null=True, blank=True, help_text="Person's date of birth."
    )
    phone_number = models.CharField(
        max_length=30, blank=True, help_text='Contact number for follow-up.'
    )
    household_size = models.PositiveIntegerField(
        null=True, blank=True, help_text='Number of people in the household.'
    )
    location = models.CharField(max_length=200, blank=True, help_text='Estate, village or ward.')
    assigned_deacon = models.CharField(
        max_length=150, blank=True,
        help_text='Deacon or deaconess assigned for follow-up, prayer and discipleship.',
    )
    story = models.TextField(
        blank=True,
        help_text='Life detail of the family. Only shown publicly after approval.',
    )
    image = models.ImageField(upload_to='impact/', blank=True, null=True)
    is_public = models.BooleanField(
        default=False,
        help_text='Approved for the public Give page. Untick to remove it again.',
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_helped', 'name']

    def save(self, *args, **kwargs):
        if not self.record_number:
            last = FundedPerson.objects.exclude(record_number='').order_by('-id').first()
            num = 1
            if last and last.record_number.startswith('OF-'):
                try:
                    num = int(last.record_number.split('-')[1]) + 1
                except (IndexError, ValueError):
                    num = FundedPerson.objects.count() + 1
            self.record_number = f"OF-{num:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.record_number})"

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = timezone.localdate()
        years = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            years -= 1
        return years


class ChurchPlant(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('planted', 'Planted'),
        ('active', 'Active'),
    ]

    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    pastor = models.CharField(max_length=150, blank=True)
    date_planted = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planted')
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_planted', 'name']

    def __str__(self):
        return self.name


def public_stories(limit=6):
    """Only records a content writer has approved for the public Give page."""
    return list(
        FundedPerson.objects.filter(is_public=True).order_by('-date_helped')[:limit]
    )


def impact_counts():
    """Live totals used by the dashboard and the public Give page."""
    return {
        'people_funded': FundedPerson.objects.count(),
        'families_fed': FundedPerson.objects.filter(category='food').count(),
        'students_sponsored': FundedPerson.objects.filter(category='scholarship').count(),
        'churches_planted': ChurchPlant.objects.filter(
            status__in=['planted', 'active']
        ).count(),
    }
