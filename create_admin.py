#!/usr/bin/env python
"""Create admin user if it doesn't exist."""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbms.settings_production')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from accounts.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_user(
        username='admin', password='admin123',
        first_name='Admin', last_name='User',
        email='admin@gracechurchmunyaka.org', role='admin'
    )
    print("Admin user created: admin / admin123")
else:
    print("Admin user already exists.")
