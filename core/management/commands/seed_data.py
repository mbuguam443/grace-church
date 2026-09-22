from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
import random

from accounts.models import User
from members.models import Family, Member
from visitors.models import Visitor
from services.models import Service
from attendance.models import Attendance
from ministries.models import Ministry
from groups.models import Group
from events.models import Event, EventRegistration
from finance.models import Transaction
from giving.models import Giving
from prayer.models import PrayerRequest
from sermons.models import Sermon
from children.models import Child, ChildAttendance
from communication.models import Announcement
from assets.models import Asset
from facilities.models import Facility, FacilityBooking


class Command(BaseCommand):
    help = 'Seed database with sample data for Grace Church Munyaka Management System'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Create demo users
        roles_data = [
            ('admin', 'Admin', 'User'),
            ('pastor', 'Pastor James', 'Mwangi'),
            ('secretary', 'Grace', 'Wanjiku'),
            ('finance', 'Peter', 'Kamau'),
            ('ministry_leader', 'Mary', 'Njeri'),
            ('group_leader', 'David', 'Ochieng'),
            ('member1', 'John', 'Doe'),
        ]
        for username, first, last in roles_data:
            if not User.objects.filter(username=username).exists():
                role_map = {
                    'admin': 'admin',
                    'pastor': 'pastor',
                    'secretary': 'secretary',
                    'finance': 'finance_officer',
                    'ministry_leader': 'ministry_leader',
                    'group_leader': 'group_leader',
                    'member1': 'member',
                }
                password_map = {
                    'admin': 'admin123',
                    'pastor': 'demo123',
                    'secretary': 'demo123',
                    'finance': 'demo123',
                    'ministry_leader': 'demo123',
                    'group_leader': 'demo123',
                    'member1': 'test123',
                }
                User.objects.create_user(
                    username=username, password=password_map[username],
                    first_name=first, last_name=last,
                    email=f'{username}@gracechurchmunyaka.org',
                    role=role_map[username]
                )

        # Create families
        families_data = [
            ('Mwangi Family', '123 Church Road', '0712345678', 'mwangi@email.com'),
            ('Kamau Family', '45 Faith Avenue', '0723456789', 'kamau@email.com'),
            ('Njeri Family', '78 Grace Street', '0734567890', 'njeri@email.com'),
            ('Ochieng Family', '32 Hope Lane', '0745678901', 'ochieng@email.com'),
            ('Wanjiku Family', '56 Blessing Road', '0756789012', 'wanjiku@email.com'),
        ]
        families = []
        for name, addr, phone, email in families_data:
            f, _ = Family.objects.get_or_create(name=name, defaults={
                'address': addr, 'phone': phone, 'email': email
            })
            families.append(f)

        # Create members
        members_data = [
            ('James', 'Mwangi', 'male', '1975-03-15', '0712345678', 'mwangi@email.com', 'active', 'married'),
            ('Grace', 'Wanjiku', 'female', '1980-07-22', '0723456789', 'wanjiku@email.com', 'active', 'married'),
            ('Peter', 'Kamau', 'male', '1985-11-08', '0734567890', 'kamau@email.com', 'active', 'single'),
            ('Mary', 'Njeri', 'female', '1990-05-30', '0745678901', 'njeri@email.com', 'active', 'single'),
            ('David', 'Ochieng', 'male', '1988-09-14', '0756789012', 'ochieng@email.com', 'active', 'married'),
            ('Faith', 'Akinyi', 'female', '1992-12-01', '0767890123', 'akinyi@email.com', 'active', 'single'),
            ('Samuel', 'Kiptoo', 'male', '1982-04-18', '0778901234', 'kiptoo@email.com', 'active', 'married'),
            ('Esther', 'Chebet', 'female', '1995-08-25', '0789012345', 'chebet@email.com', 'active', 'single'),
            ('Joseph', 'Mutua', 'male', '1978-02-10', '0790123456', 'mutua@email.com', 'active', 'married'),
            ('Hannah', 'Muthoni', 'female', '1993-06-17', '0701234567', 'muthoni@email.com', 'active', 'single'),
        ]
        members = []
        for i, (first, last, gender, dob, phone, email, status, marital) in enumerate(members_data):
            m, created = Member.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first, 'last_name': last, 'gender': gender,
                    'date_of_birth': dob, 'phone': phone, 'membership_status': status,
                    'marital_status': marital, 'date_joined': date(2020, 1, 1) + timedelta(days=random.randint(0, 1000)),
                    'family': families[i % len(families)] if i < 5 else None,
                    'occupation': random.choice(['Teacher', 'Engineer', 'Doctor', 'Business', 'Farmer', 'Accountant']),
                    'baptism_status': True,
                }
            )
            members.append(m)

        # Create visitors
        visitors_data = [
            ('John', 'Doe', '0711111111', date.today() - timedelta(days=7), 'Friend'),
            ('Jane', 'Smith', '0722222222', date.today() - timedelta(days=3), 'Social Media'),
            ('Mike', 'Brown', '0733333333', date.today() - timedelta(days=1), 'Walk-in'),
        ]
        for first, last, phone, vdate, heard in visitors_data:
            Visitor.objects.get_or_create(
                first_name=first, last_name=last, visit_date=vdate,
                defaults={'phone': phone, 'how_they_heard': heard, 'follow_up_status': 'new'}
            )

        # Create services
        services_data = [
            ('Sunday Service', date.today() - timedelta(days=7), '09:00', '12:00', 'Main Hall', 'Pastor James', 'Walking by Faith', 'Hebrews 11:1'),
            ('Wednesday Service', date.today() - timedelta(days=4), '18:00', '20:00', 'Main Hall', 'Pastor James', 'Prayer Night', 'James 5:16'),
            ('Friday Prayer', date.today() - timedelta(days=2), '18:00', '20:00', 'Prayer Room', 'Pastor James', 'Fasting & Prayer', 'Matthew 17:21'),
            ('Sunday Service', date.today(), '09:00', '12:00', 'Main Hall', 'Pastor James', 'God\'s Grace', 'Ephesians 2:8'),
        ]
        services = []
        for name, sdate, start, end, loc, preacher, theme, verse in services_data:
            s, _ = Service.objects.get_or_create(
                name=name, date=sdate,
                defaults={'start_time': start, 'end_time': end, 'location': loc, 'preacher': preacher, 'theme': theme, 'bible_verse': verse}
            )
            services.append(s)

        # Create attendance
        for service in services:
            for member in members[:random.randint(5, 8)]:
                Attendance.objects.get_or_create(service=service, member=member)

        # Create ministries
        ministries_data = [
            ('Youth Ministry', 'Empowering the next generation'),
            ('Men\'s Ministry', 'Building godly men'),
            ('Women\'s Ministry', 'Nurturing women of faith'),
            ('Children\'s Ministry', 'Teaching kids the word'),
            ('Worship Team', 'Leading the congregation in praise'),
            ('Media Team', 'Technical and communications'),
            ('Ushers Ministry', 'Welcoming and guiding'),
            ('Evangelism', 'Spreading the gospel'),
        ]
        for name, desc in ministries_data:
            m, _ = Ministry.objects.get_or_create(name=name, defaults={'description': desc, 'leader': random.choice(members)})
            m.members.set(random.sample(members, min(4, len(members))))

        # Create groups
        groups_data = (
            ('Alpha Cell Group', 'Monday', '19:00', 'Zone A'),
            ('Beta Cell Group', 'Tuesday', '19:00', 'Zone B'),
            ('Gamma Cell Group', 'Wednesday', '19:00', 'Zone C'),
        )
        for name, day, time, loc in groups_data:
            g, _ = Group.objects.get_or_create(
                name=name,
                defaults={'meeting_day': day, 'meeting_time': time, 'location': loc, 'leader': random.choice(members)}
            )
            g.members.set(random.sample(members, min(5, len(members))))

        # Create events
        events_data = (
            ('Annual Conference 2026', 'A week of spiritual renewal', date.today() + timedelta(days=30), 'Main Hall', 500),
            ('Youth Retreat', 'Teenagers getaway', date.today() + timedelta(days=14), 'Camp Ground', 100),
            ('Women\'s Conference', 'Women of purpose', date.today() + timedelta(days=45), 'Main Hall', 200),
            ('Easter Service', 'Celebrating resurrection', date.today() + timedelta(days=60), 'Main Hall', 0),
        )
        for name, desc, edate, loc, cap in events_data:
            e, _ = Event.objects.get_or_create(
                name=name, date=edate,
                defaults={'description': desc, 'location': loc, 'capacity': cap, 'organizer': random.choice(members)}
            )

        # Create finance transactions
        income_cats = ['tithe', 'offering', 'donation', 'building_fund', 'missions']
        expense_cats = ['salaries', 'rent', 'electricity', 'water', 'transport', 'equipment']
        for i in range(20):
            tdate = date.today() - timedelta(days=random.randint(0, 60))
            Transaction.objects.create(
                transaction_type='income',
                amount=random.randint(500, 50000),
                category=random.choice(income_cats),
                description=f'Income record {i+1}',
                date=tdate,
                member=random.choice(members),
            )
        for i in range(10):
            tdate = date.today() - timedelta(days=random.randint(0, 60))
            Transaction.objects.create(
                transaction_type='expense',
                amount=random.randint(200, 20000),
                category=random.choice(expense_cats),
                description=f'Expense record {i+1}',
                date=tdate,
            )

        # Create giving records
        for i in range(15):
            Giving.objects.create(
                member=random.choice(members),
                amount=random.randint(100, 10000),
                giving_category=random.choice(['tithe', 'offering', 'donation']),
                date=date.today() - timedelta(days=random.randint(0, 60)),
                payment_method=random.choice(['cash', 'mpesa', 'bank']),
                reference_number=f'REF{random.randint(10000, 99999)}',
            )

        # Create prayer requests
        prayers_data = (
            ('Healing', 'Pray for my mother\'s health recovery', False),
            ('Job', 'Need a new job opportunity', False),
            ('Family', 'Peace in my marriage', True),
            ('Studies', 'Success in my exams', False),
            ('Travel', 'Safe journey for my brother', False),
        )
        for cat, req, conf in prayers_data:
            PrayerRequest.objects.get_or_create(
                title=cat, defaults={
                    'request': req, 'category': cat.lower(),
                    'member': random.choice(members), 'is_confidential': conf,
                    'status': random.choice(['new', 'assigned', 'in_progress', 'completed'])
                }
            )

        # Create sermons
        sermons_data = (
            ('Walking by Faith', 'Pastor James Mwangi', 'Hebrews 11:1', 'Faith is the substance of things hoped for.'),
            ('The Power of Prayer', 'Pastor James Mwangi', 'James 5:16', 'The effective prayer of a righteous person can accomplish much.'),
            ('God\'s Grace', 'Pastor James Mwangi', 'Ephesians 2:8', 'By grace you are saved through faith.'),
            ('Overcoming Fear', 'Pastor James Mwangi', '2 Timothy 1:7', 'God has not given us a spirit of fear.'),
        )
        for title, speaker, verse, desc in sermons_data:
            Sermon.objects.get_or_create(
                title=title, defaults={
                    'speaker': speaker, 'bible_verse': verse, 'description': desc,
                    'date': date.today() - timedelta(days=random.randint(0, 30))
                }
            )

        # Create children
        children_data = (
            ('Baby', 'Mwangi', '2018-05-10', 'female'),
            ('Junior', 'Kamau', '2017-08-15', 'male'),
            ('Hope', 'Ochieng', '2019-03-20', 'female'),
            ('Blessing', 'Mutua', '2016-11-25', 'female'),
        )
        for first, last, dob, gender in children_data:
            Child.objects.get_or_create(
                first_name=first, last_name=last,
                defaults={'date_of_birth': dob, 'gender': gender, 'parent': random.choice(members), 'school_class': f'Class {random.randint(1, 4)}'}
            )

        # Create announcements
        announcements_data = (
            ('Sunday Service Time Change', 'Service will now start at 9:00 AM', 'everyone'),
            ('Youth Meeting', 'All youth members meeting Saturday at 4 PM', 'youth'),
            ('Prayer Week', 'Join us for a week of fasting and prayer', 'members'),
        )
        for title, msg, target in announcements_data:
            Announcement.objects.get_or_create(title=title, defaults={'message': msg, 'target_audience': target})

        # Create assets
        assets_data = (
            ('Projector', 'Electronics', '2023-01-15', 80000, 'excellent', 'Main Hall'),
            ('Sound System', 'Electronics', '2022-06-10', 150000, 'good', 'Main Hall'),
            ('Office Chairs (50)', 'Furniture', '2021-03-20', 75000, 'good', 'Main Hall'),
            ('Camera', 'Electronics', '2024-01-10', 45000, 'excellent', 'Media Room'),
            ('Piano', 'Musical', '2020-09-05', 120000, 'good', 'Main Hall'),
        )
        for name, cat, pdate, val, cond, loc in assets_data:
            Asset.objects.get_or_create(
                name=name, defaults={
                    'category': cat, 'purchase_date': pdate, 'value': val,
                    'condition': cond, 'location': loc
                }
            )

        # Create facilities
        facilities_data = (
            ('Main Hall', 'Main worship hall', 500, 'Building A'),
            ('Conference Room', 'Meetings and conferences', 50, 'Building B'),
            ('Children\'s Classroom', 'Sunday school classes', 30, 'Building C'),
            ('Prayer Room', 'Private prayer room', 20, 'Building A'),
        )
        for name, desc, cap, loc in facilities_data:
            Facility.objects.get_or_create(name=name, defaults={'description': desc, 'capacity': cap, 'location': loc})

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
