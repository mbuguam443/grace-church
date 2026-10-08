from datetime import datetime
from uuid import uuid4

from django.db import models
from django.utils import timezone

from members.models import Member
from finance.models import Transaction


class Giving(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank'),
        ('card', 'Card'),
        ('online', 'Online'),
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

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='givings', null=True, blank=True)
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
        return f"{self.donor_name or 'Unknown'} - {self.amount} - {self.date}"

    @property
    def donor_name(self):
        if self.member:
            parts = [p for p in (self.member.first_name, self.member.middle_name, self.member.last_name) if p]
            return ' '.join(parts)
        online = getattr(self, 'online_record', None)
        if online is not None:
            return online.name
        return ''


class OnlineGiving(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('voided', 'Voided'),
    ]
    FREQUENCY_CHOICES = [
        ('one_time', 'One-time'),
        ('monthly', 'Monthly'),
        ('annual', 'Annually'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    giving_category = models.CharField(max_length=30, choices=Giving.GIVING_CATEGORIES)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='one_time')
    note = models.TextField(blank=True)
    reference_number = models.CharField(max_length=40, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='online_givings')
    giving = models.OneToOneField(Giving, on_delete=models.SET_NULL, null=True, blank=True, related_name='online_record')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.amount} - {self.reference_number}"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = 'GCG-' + datetime.now().strftime('%Y%m%d%H%M%S') + '-' + uuid4().hex[:4].upper()
        super().save(*args, **kwargs)

    def post_to_finance(self):
        """Create the linked Giving record and income Transaction."""
        member = None
        email = (self.email or '').strip().lower()
        if email:
            member = Member.objects.filter(email__iexact=email).first()
        today = timezone.localdate()
        notes = f"Online giving via website - {self.name} <{self.email}>"
        if self.note:
            notes += f" | {self.note}"
        transaction = Transaction.objects.create(
            transaction_type='income',
            amount=self.amount,
            category=self.giving_category,
            description=f"Online giving ({self.name})",
            date=today,
            member=member,
        )
        giving = Giving.objects.create(
            member=member,
            amount=self.amount,
            giving_category=self.giving_category,
            date=today,
            payment_method='online',
            reference_number=self.reference_number,
            notes=notes,
            transaction=transaction,
        )
        self.member = member
        self.giving = giving
        self.status = 'confirmed'
        self.save(update_fields=['member', 'giving', 'status'])
        return giving, transaction
