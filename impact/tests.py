from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import User
from core.models import ChurchSetting, RoleModulePermission

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
        self.admin = User.objects.create_superuser(
            'impact_admin', 'impact_admin@test.com', 'test123', role='super_admin'
        )

    def test_list_pages_require_login(self):
        client = Client()
        for name in ['impact:funded-list', 'impact:churchplant-list']:
            response = client.get(reverse(name))
            self.assertEqual(response.status_code, 302, name)

    def test_admin_can_manage_records(self):
        self.client.force_login(self.admin)

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
        self.client.force_login(self.admin)
        FundedPerson.objects.create(name='Jane', category='food')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['impact_counts']['people_funded'], 1)


class YourImpactStatsTests(TestCase):
    def setUp(self):
        self.client = Client()
        ChurchSetting.get_settings()
        self.admin = User.objects.create_superuser(
            'stats_admin', 'stats_admin@test.com', 'test123', role='super_admin'
        )
        self.sponsor = User.objects.create_user(
            'donor2', 'donor2@test.com', 'test123', role='sponsor'
        )

    def test_admin_can_open_and_save_the_control(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('impact:stats'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'impact_1_label')
        self.assertContains(response, 'impact_2_value')
        self.assertContains(response, 'Families Fed')
        self.assertContains(response, 'Students Sponsored')
        self.assertContains(response, 'Churches Planted')

        response = self.client.post(reverse('impact:stats'), {
            'impact_1_value': '750', 'impact_1_label': 'Families Fed',
            'impact_1_note': 'meals shared this year',
            'impact_2_value': '45', 'impact_2_label': 'Students Sponsored',
            'impact_2_note': 'in school today',
            'impact_3_value': '8', 'impact_3_label': 'Churches Planted',
            'impact_3_note': 'across Kenya',
        })
        self.assertEqual(response.status_code, 302)

        settings_obj = ChurchSetting.get_settings()
        self.assertEqual(settings_obj.impact_1_value, '750')
        self.assertEqual(settings_obj.impact_2_label, 'Students Sponsored')
        self.assertEqual(settings_obj.impact_3_note, 'across Kenya')

        give = self.client.get(reverse('public:give'))
        self.assertEqual(str(give.context['impact_1_display']), '750')

    def test_sponsor_cannot_change_the_control(self):
        self.client.force_login(self.sponsor)
        response = self.client.get(reverse('impact:stats'))
        self.assertEqual(response.status_code, 403)
        response = self.client.post(reverse('impact:stats'), {
            'impact_1_value': '999999', 'impact_1_label': 'Hacked',
            'impact_2_value': '1', 'impact_2_label': 'x',
            'impact_3_value': '1', 'impact_3_label': 'y',
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(ChurchSetting.get_settings().impact_1_value, '500+')

    def test_requires_login(self):
        response = Client().get(reverse('impact:stats'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_offers_the_control_to_admin_only(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('dashboard:index'))
        self.assertContains(response, reverse('impact:stats'))

        self.client.force_login(self.sponsor)
        response = self.client.get(reverse('dashboard:index'))
        self.assertNotContains(response, 'Edit Your Impact')

        member = User.objects.create_user('member2', 'member2@test.com', 'test123', role='member')
        self.client.force_login(member)
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Edit Your Impact')


class SponsorAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        ChurchSetting.get_settings()
        self.sponsor = User.objects.create_user(
            'donor1', 'donor@test.com', 'test123', role='sponsor'
        )
        self.member = User.objects.create_user(
            'member1', 'member@test.com', 'test123', role='member'
        )
        FundedPerson.objects.create(name='Jane', category='food')
        ChurchPlant.objects.create(name='Zone-T', status='planted')

    def test_sponsor_role_is_seeded_with_impact_module(self):
        self.assertTrue(
            RoleModulePermission.objects.filter(role='sponsor', module='impact').exists()
        )

    def test_sponsor_sees_sponsorship_dashboard(self):
        self.client.force_login(self.sponsor)
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_sponsor_view'])
        self.assertContains(response, 'Sponsorship Dashboard')
        self.assertContains(response, 'Give Now')
        self.assertContains(response, 'Recently Funded')

    def test_sponsor_sidebar_only_offers_outreach(self):
        self.client.force_login(self.sponsor)
        response = self.client.get(reverse('dashboard:index'))
        self.assertContains(response, 'Outreach')
        self.assertContains(response, reverse('impact:funded-list'))
        for section in ['Management', 'Church Life', 'Finance', 'Operations', 'Administration']:
            self.assertNotContains(response, 'sidebar-section">%s<' % section)

    def test_sponsor_can_read_outreach_records(self):
        self.client.force_login(self.sponsor)
        for name in ['impact:funded-list', 'impact:churchplant-list']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)
        response = self.client.get(reverse('impact:funded-list'))
        self.assertNotContains(response, 'Add Record')

    def test_sponsor_cannot_create_records(self):
        self.client.force_login(self.sponsor)
        response = self.client.post(reverse('impact:funded-create'), {
            'name': 'Sneaky', 'category': 'food',
            'date_helped': '2026-10-06', 'status': 'active', 'note': '',
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(FundedPerson.objects.filter(name='Sneaky').exists())

    def test_sponsor_is_blocked_from_other_modules(self):
        self.client.force_login(self.sponsor)
        for path in ['/members/', '/finance/', '/giving/', '/reports/', '/core/settings/',
                     '/accounts/users/', '/accounts/permissions/']:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 302, path)
            self.assertEqual(response.url, reverse('dashboard:index'), path)

    def test_sponsor_can_use_public_site(self):
        self.client.force_login(self.sponsor)
        for path in ['/', '/give-now/', '/about-us/']:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)

    def test_other_roles_are_not_blocked(self):
        self.client.force_login(self.member)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
