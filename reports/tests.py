from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import User
from impact.models import FundedPerson


class ImpactReportTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            'report_admin', 'report_admin@test.com', 'test123', role='super_admin'
        )
        FundedPerson.objects.create(name='Jane Doe', category='food', location='Theta')
        FundedPerson.objects.create(name='Peter Kamau', category='scholarship', location='Ruiru')

    def test_impact_report_requires_login(self):
        response = Client().get(reverse('reports:impact-report'))
        self.assertEqual(response.status_code, 302)

    def test_impact_report_page_lists_people(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('reports:impact-report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Doe')
        self.assertContains(response, 'Peter Kamau')

    def test_impact_report_pdf_downloads(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('reports:impact-report') + '?format=pdf')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_impact_report_csv_downloads(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('reports:impact-report') + '?export=csv')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('Jane Doe', response.content.decode())

    def test_single_person_report_html(self):
        self.client.force_login(self.admin)
        person = FundedPerson.objects.get(name='Jane Doe')
        response = self.client.get(reverse('reports:funded-person-report', args=[person.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Doe')
        self.assertContains(response, person.record_number)

    def test_single_person_report_pdf_downloads(self):
        self.client.force_login(self.admin)
        person = FundedPerson.objects.get(name='Peter Kamau')
        response = self.client.get(
            reverse('reports:funded-person-report', args=[person.pk]) + '?format=pdf'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_single_person_report_handles_missing(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('reports:funded-person-report', args=[9999]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'could not be found', status_code=200)
