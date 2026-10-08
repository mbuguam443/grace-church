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

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='food')
    date_helped = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    household_size = models.PositiveIntegerField(
        null=True, blank=True, help_text='Number of people in the household.'
    )
    location = models.CharField(max_length=200, blank=True, help_text='Estate, village or ward.')
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

    def __str__(self):
        return self.name


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
