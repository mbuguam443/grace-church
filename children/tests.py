from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import User
from members.models import Member

from .models import Child


class ChildTeacherDropdownTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            'child_admin', 'child_admin@test.com', 'test123', role='super_admin'
        )
        self.teacher = Member.objects.create(
            first_name='Alice', last_name='Wambui', gender='female',
        )

    def test_teacher_dropdown_lists_active_members(self):
        Member.objects.create(first_name='Inactive', last_name='Person', gender='male',
                              membership_status='inactive')
        self.client.force_login(self.admin)
        response = self.client.get(reverse('children:child_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice Wambui')
        teacher_qs = response.context['form'].fields['teacher'].queryset
        self.assertIn(self.teacher, teacher_qs)
        self.assertFalse(teacher_qs.filter(last_name='Person').exists())

    def test_child_can_be_saved_with_teacher_member(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('children:child_create'), {
            'first_name': 'Baby', 'last_name': 'Wambui',
            'date_of_birth': '2018-05-10', 'gender': 'female',
            'teacher': self.teacher.pk,
            'school_class': 'Class 1', 'is_active': 'on',
        })
        self.assertEqual(response.status_code, 302)
        child = Child.objects.get(first_name='Baby')
        self.assertEqual(child.teacher, self.teacher)
        self.assertEqual(child.teacher_name, 'Alice Wambui')
