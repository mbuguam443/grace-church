from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import User
from members.models import Member

from .models import BibleStudyNote


class BibleStudyTeacherDropdownTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            'study_admin', 'study_admin@test.com', 'test123', role='super_admin'
        )
        self.teacher = Member.objects.create(
            first_name='John', last_name='Omondi', gender='male',
        )

    def test_teacher_dropdown_lists_active_members(self):
        Member.objects.create(first_name='Inactive', last_name='Person', gender='male',
                              membership_status='inactive')
        self.client.force_login(self.admin)
        response = self.client.get(reverse('bible_study:study_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Omondi')
        self.assertNotContains(response, 'Inactive Person')

    def test_study_saves_teacher_member(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('bible_study:study_create'), {
            'title': 'Faith', 'bible_verse': 'Hebrews 11:1',
            'study_date': '2026-10-06', 'teacher': self.teacher.pk,
            'content': 'study body', 'is_active': 'on',
        })
        self.assertEqual(response.status_code, 302)
        study = BibleStudyNote.objects.get(title='Faith')
        self.assertEqual(study.teacher, self.teacher)
        self.assertEqual(study.teacher_name, 'John Omondi')
