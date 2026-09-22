#!/usr/bin/env python
"""
Grace Church Munyaka - Web Management Script (browser-run, file-based cPanel deploy).
Run via browser: http://yourdomain.com/manage_web.py
Uses settings_production (MySQL via PyMySQL) — no SSH needed.
"""
import os
import sys

# Change to project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbms.settings_production')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.core.management import call_command
from django.http import HttpResponse
from django.urls import path
from django.conf import settings
from django.core.wsgi import get_wsgi_application

urlpatterns = [
    path('', lambda r: HttpResponse("""
        <h1>Grace Church Munyaka Management</h1>
        <p><a href="/manage/migrate/">Run Migrations</a></p>
        <p><a href="/manage/collectstatic/">Collect Static Files</a></p>
        <p><a href="/manage/seed/">Seed Demo Data</a></p>
        <p><a href="/manage/setup-all/">Run All Setup</a></p>
    """)),
    path('migrate/', lambda r: (call_command('migrate'), HttpResponse("Migrations completed!"))[1]),
    path('collectstatic/', lambda r: (call_command('collectstatic', '--noinput'), HttpResponse("Static files collected!"))[1]),
    path('seed/', lambda r: (call_command('seed_data'), HttpResponse("Demo data seeded!"))[1]),
    path('setup-all/', lambda r: (call_command('migrate'), call_command('collectstatic', '--noinput'), call_command('seed_data'), HttpResponse("All setup completed!"))[3]),
]

if __name__ == '__main__':
    print("Run management commands:")
    print("1. Migrate: python manage.py migrate --settings=fbms.settings_production")
    print("2. Collect Static: python manage.py collectstatic --noinput --settings=fbms.settings_production")
    print("3. Seed Data: python manage.py seed_data --settings=fbms.settings_production")
