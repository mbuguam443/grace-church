from django.db import models
from members.models import Member


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    INCOME_CATEGORIES = [
        ('tithe', 'Tithe'),
        ('offering', 'Offering'),
        ('donation', 'Donation'),
        ('building_fund', 'Building Fund'),
        ('missions', 'Missions'),
        ('special_contribution', 'Special Contribution'),
        ('other', 'Other'),
    ]
    EXPENSE_CATEGORIES = [
        ('salaries', 'Salaries'),
        ('rent', 'Rent'),
        ('electricity', 'Electricity'),
        ('water', 'Water'),
        ('transport', 'Transport'),
        ('equipment', 'Equipment'),
        ('maintenance', 'Maintenance'),
        ('events', 'Events'),
        ('other', 'Other'),
    ]

    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    date = models.DateField()
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    recorded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} - {self.date}"
