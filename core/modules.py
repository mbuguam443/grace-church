# Sidebar modules that the admin can show/hide per role.
MODULES = [
    ('members', 'Members'),
    ('families', 'Families'),
    ('visitors', 'Visitors'),
    ('services', 'Services'),
    ('attendance', 'Attendance'),
    ('ministries', 'Ministries'),
    ('groups', 'Groups'),
    ('children', 'Children'),
    ('events', 'Events'),
    ('sermons', 'Sermons'),
    ('songs', 'Praise & Worship'),
    ('bible_study', 'Bible Study'),
    ('sunday_school', 'Sunday School'),
    ('announcements', 'Announcements'),
    ('finance', 'Finance'),
    ('giving', 'Giving'),
    ('assets', 'Assets'),
    ('facilities', 'Facilities'),
    ('reports', 'Reports'),
    ('users', 'User Management'),
    ('settings', 'Settings'),
]

MODULE_KEYS = [key for key, label in MODULES]

# Modules every logged-in user should keep (the landing area).
ALWAYS_VISIBLE = ['events', 'sermons', 'songs', 'bible_study', 'sunday_school', 'ministries', 'announcements']