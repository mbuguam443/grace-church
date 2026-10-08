from datetime import date
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import User
from members.models import Member

from .models import Giving, OnlineGiving


class DonorNameTests(TestCase):
    def test_uses_member_name(self):
        member = Member.objects.create(first_name='Jane', middle_name='Grace', last_name='Doe')
        giving = Giving.objects.create(
            member=member, amount=Decimal('1000.00'), giving_category='tithe',
            date=date.today(), payment_method='cash',
        )
        self.assertEqual(giving.donor_name, 'Jane Grace Doe')

    def test_uses_online_record_name_when_member_is_missing(self):
        giving = Giving.objects.create(
            member=None, amount=Decimal('500.00'), giving_category='offering',
            date=date.today(), payment_method='online',
        )
        OnlineGiving.objects.create(
            name='Website Donor', email='donor@test.com', amount=Decimal('500.00'),
            giving_category='offering', giving=giving,
        )
        self.assertEqual(giving.donor_name, 'Website Donor')

    def test_empty_when_no_member_and_no_online_record(self):
        giving = Giving.objects.create(
            member=None, amount=Decimal('250.00'), giving_category='donation',
            date=date.today(), payment_method='cash',
        )
        self.assertEqual(giving.donor_name, '')


class GivingListTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.finance = User.objects.create_user(
            'finance1', 'finance1@test.com', 'test123', role='finance_officer'
        )
        self.member_user = User.objects.create_user(
            'plain1', 'plain1@test.com', 'test123', role='member'
        )

    def test_list_shows_online_gifts_without_crashing(self):
        member = Member.objects.create(first_name='Jane', last_name='Doe')
        Giving.objects.create(
            member=member, amount=Decimal('1000.00'), giving_category='tithe',
            date=date.today(), payment_method='cash',
        )
        online_giving = Giving.objects.create(
            member=None, amount=Decimal('500.00'), giving_category='offering',
            date=date.today(), payment_method='online',
        )
        OnlineGiving.objects.create(
            name='Website Donor', email='donor@test.com', amount=Decimal('500.00'),
            giving_category='offering', giving=online_giving,
        )

        self.client.force_login(self.finance)
        response = self.client.get(reverse('giving:giving-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Website Donor')
        self.assertContains(response, 'Jane Doe')

    def test_list_requires_finance_role(self):
        self.client.force_login(self.member_user)
        response = self.client.get(reverse('giving:giving-list'))
        self.assertEqual(response.status_code, 403)

    def test_online_list_requires_login(self):
        response = Client().get(reverse('giving:online-giving-list'))
        self.assertEqual(response.status_code, 302)
