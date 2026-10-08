import ast
from pathlib import Path

from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse
from accounts.models import User
from members.models import Family, Member
from .models import RoleModulePermission


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'testpass123', role='super_admin')
        self.member_user = User.objects.create_user('member1', 'member@test.com', 'testpass123', role='member')

    def test_login_page_loads(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(reverse('accounts:login'), {'username': 'admin', 'password': 'testpass123'})
        self.assertEqual(response.status_code, 302)

    def test_login_invalid(self):
        response = self.client.post(reverse('accounts:login'), {'username': 'admin', 'password': 'wrong'})
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_accessible_when_logged_in(self):
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)


class MemberModelTests(TestCase):
    def test_member_number_auto_generated(self):
        member = Member.objects.create(
            first_name='John', last_name='Doe', gender='male'
        )
        self.assertTrue(member.member_number.startswith('GC-'))

    def test_member_str(self):
        member = Member.objects.create(
            first_name='John', last_name='Doe', gender='male'
        )
        self.assertIn('John Doe', str(member))


class MemberViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'testpass123', role='super_admin')
        self.client.login(username='admin', password='testpass123')

    def test_member_list_view(self):
        response = self.client.get(reverse('members:member-list'))
        self.assertEqual(response.status_code, 200)

    def test_member_create_view(self):
        response = self.client.get(reverse('members:member-create'))
        self.assertEqual(response.status_code, 200)

    def test_member_create_post(self):
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'gender': 'female',
            'phone': '0712345678',
            'email': 'jane@test.com',
            'membership_status': 'active',
            'marital_status': 'single',
            'membership_type': 'full',
        }
        response = self.client.post(reverse('members:member-create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Member.objects.filter(email='jane@test.com').exists())

    def test_member_detail_view(self):
        member = Member.objects.create(first_name='Test', last_name='User', gender='male')
        response = self.client.get(reverse('members:member-detail', kwargs={'pk': member.pk}))
        self.assertEqual(response.status_code, 200)

    def test_member_edit_view(self):
        member = Member.objects.create(first_name='Test', last_name='User', gender='male')
        response = self.client.get(reverse('members:member-update', kwargs={'pk': member.pk}))
        self.assertEqual(response.status_code, 200)

    def test_member_delete_view(self):
        member = Member.objects.create(first_name='Test', last_name='Delete', gender='male')
        response = self.client.post(reverse('members:member-delete', kwargs={'pk': member.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Member.objects.filter(pk=member.pk).exists())


class FamilyViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'testpass123', role='super_admin')
        self.client.login(username='admin', password='testpass123')

    def test_family_list_view(self):
        response = self.client.get(reverse('members:family-list'))
        self.assertEqual(response.status_code, 200)

    def test_family_create(self):
        data = {'name': 'Test Family', 'address': '123 Test St', 'phone': '0712345678'}
        response = self.client.post(reverse('members:family-create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Family.objects.filter(name='Test Family').exists())


class PermissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.member_user = User.objects.create_user('member1', 'member@test.com', 'testpass123', role='member')

    def test_member_cannot_access_admin(self):
        self.client.login(username='member1', password='testpass123')
        response = self.client.get(reverse('members:member-create'))
        self.assertIn(response.status_code, [302, 403])

    def test_public_pages_accessible(self):
        response = self.client.get(reverse('public:home'))
        self.assertEqual(response.status_code, 200)

    def test_contact_page_accessible(self):
        response = self.client.get(reverse('public:contact'))
        self.assertEqual(response.status_code, 200)


class ProductionSettingsSyncTests(SimpleTestCase):
    """The server runs fbms.settings_production - it must not drift from settings.py."""

    def list_setting(self, filename, name):
        path = Path(__file__).resolve().parent.parent / 'fbms' / filename
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in tree.body:
            if isinstance(node, ast.Assign):
                if any(getattr(target, 'id', None) == name for target in node.targets):
                    return [item.value for item in node.value.elts]
        self.fail('%s not found in fbms/%s' % (name, filename))

    def test_production_has_every_installed_app(self):
        dev = self.list_setting('settings.py', 'INSTALLED_APPS')
        prod = self.list_setting('settings_production.py', 'INSTALLED_APPS')
        missing = [app for app in dev if app not in prod]
        self.assertEqual(
            missing, [],
            'fbms/settings_production.py is missing INSTALLED_APPS: %s' % missing,
        )

    def test_production_has_every_middleware(self):
        dev = self.list_setting('settings.py', 'MIDDLEWARE')
        prod = self.list_setting('settings_production.py', 'MIDDLEWARE')
        missing = [mw for mw in dev if mw not in prod]
        self.assertEqual(
            missing, [],
            'fbms/settings_production.py is missing MIDDLEWARE: %s' % missing,
        )


class OutreachSidebarTests(TestCase):
    """Outreach must be reachable even when a role's saved permissions predate it."""

    def setUp(self):
        self.client = Client()
        self.writer = User.objects.create_user(
            'writer1', 'writer1@test.com', 'test123', role='secretary'
        )
        self.finance = User.objects.create_user(
            'finance2', 'finance2@test.com', 'test123', role='finance_officer'
        )

    def _old_permissions_without_impact(self, role):
        RoleModulePermission.objects.filter(role=role).delete()
        RoleModulePermission.objects.bulk_create([
            RoleModulePermission(role=role, module='finance'),
            RoleModulePermission(role=role, module='giving'),
        ])

    def test_content_writer_sees_outreach_despite_old_permissions(self):
        self._old_permissions_without_impact('secretary')
        self.client.force_login(self.writer)
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'sidebar-section">Outreach<')
        self.assertContains(response, reverse('impact:funded-list'))

    def test_non_writer_without_impact_module_does_not_see_outreach(self):
        self._old_permissions_without_impact('finance_officer')
        self.client.force_login(self.finance)
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'sidebar-section">Outreach<')

    def test_finance_role_can_still_reach_its_own_modules(self):
        self._old_permissions_without_impact('finance_officer')
        self.client.force_login(self.finance)
        response = self.client.get(reverse('giving:giving-list'))
        self.assertEqual(response.status_code, 200)
