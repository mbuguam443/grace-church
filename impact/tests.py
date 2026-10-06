from django.test import TestCase, Client
from django.urls import reverse

from core.models import ChurchSetting

from .models import ChurchPlant, FundedPerson, impact_counts


class ImpactCountTests(TestCase):
    def test_counts_by_category_and_status(self):
        FundedPerson.objects.create(name='Jane', category='food')
        FundedPerson.objects.create(name='Peter', category='food')
        FundedPerson.objects.create(name='Mercy', category='scholarship')
        FundedPerson.objects.create(name='Ali', category='medical')
        ChurchPlant.objects.create(name='Zone-T', status='planted')
        ChurchPlant.objects.create(name='Upcoming', status='planned')

        counts = impact_counts()
        self.assertEqual(counts['people_funded'], 4)
        self.assertEqual(counts['families_fed'], 2)
        self.assertEqual(counts['students_sponsored'], 1)
        self.assertEqual(counts['churches_planted'], 1)


class PublicGivePageTests(TestCase):
    def setUp(self):
        self.client = Client()
        ChurchSetting.get_settings()

    def test_falls_back_to_settings_when_no_records(self):
        response = self.client.get(reverse('public:give'))
        self.assertEqual(str(response.context['impact_1_display']), '500+')
        self.assertEqual(str(response.context['impact_2_display']), '120')
        self.assertEqual(str(response.context['impact_3_display']), '12')

    def test_uses_live_counts_when_records_exist(self):
        FundedPerson.objects.create(name='Jane', category='food')
        FundedPerson.objects.create(name='Mercy', category='scholarship')
        ChurchPlant.objects.create(name='Zone-T', status='planted')

        response = self.client.get(reverse('public:give'))
        self.assertEqual(str(response.context['impact_1_display']), '1')
        self.assertEqual(str(response.context['impact_2_display']), '1')
        self.assertEqual(str(response.context['impact_3_display']), '1')


class ImpactViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_list_pages_require_login(self):
        for name in ['impact:funded-list', 'impact:churchplant-list']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302, name)

    def test_admin_can_manage_records(self):
        User = __import__('accounts.models', fromlist=['User']).User
        self.client.force_login(
            User.objects.create_superuser('admin', 'admin@test.com', 'test123', role='super_admin')
        )

        response = self.client.post(reverse('impact:funded-create'), {
            'name': 'Jane Doe',
            'category': 'food',
            'date_helped': '2026-10-06',
            'status': 'active',
            'note': '',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(FundedPerson.objects.filter(name='Jane Doe').exists())

        response = self.client.post(reverse('impact:churchplant-create'), {
            'name': 'Zone-T Church',
            'location': 'Ruiru',
            'pastor': 'Harry',
            'date_planted': '2025-06-29',
            'status': 'planted',
            'note': '',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ChurchPlant.objects.filter(name='Zone-T Church').exists())

    def test_dashboard_shows_impact_counts(self):
        User = __import__('accounts.models', fromlist=['User']).User
        self.client.force_login(
            User.objects.create_superuser('admin2', 'admin2@test.com', 'test123', role='super_admin')
        )
        FundedPerson.objects.create(name='Jane', category='food')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['impact_counts']['people_funded'], 1)
