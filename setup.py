#!/usr/bin/env python
"""
Grace Church Munyaka - Run All Setup Commands
This script runs all necessary setup commands for deployment.
"""
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbms.settings_production')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.core.management import call_command

print("=" * 50)
print("Grace Church Munyaka - Running Setup Commands")
print("=" * 50)

print("\n1. Running migrations...")
call_command('migrate')
print("   Migrations completed!")

print("\n2. Collecting static files...")
call_command('collectstatic', '--noinput')
print("   Static files collected!")

print("\n3. Seeding demo data...")
call_command('seed_data')
print("   Demo data seeded!")

print("\n" + "=" * 50)
print("ALL SETUP COMPLETED SUCCESSFULLY!")
print("=" * 50)
print("\nDefault login credentials:")
print("  Admin: admin / admin123")
print("  Pastor: pastor / demo123")
print("  Member: member1 / test123")
print("  Secretary: secretary / demo123")
print("  Finance: finance / demo123")
