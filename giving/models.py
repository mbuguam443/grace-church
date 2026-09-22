from django.db import models
from members.models import Member
from finance.models import Transaction


class Giving(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank'),
        ('card', 'Card'),
        ('other', 'Other'),
    ]
    GIVING_CATEGORIES = [
        ('tithe', 'Tithe'),
        ('offering', 'Offering'),
        ('donation', 'Donation'),
        ('building_fund', 'Building Fund'),
        ('missions', 'Missions'),
        ('special_contribution', 'Special Contribution'),
        ('other', 'Other'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='givings')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    giving_category = models.CharField(max_length=30, choices=GIVING_CATEGORIES)
    date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='giving_record')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.member} - {self.amount} - {self.date}"
