#!/usr/bin/env python
"""
Grace Church Munyaka - Update Script
Run this after pushing changes to GitHub to update cPanel.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbms.settings_production')

print("=" * 50)
print("Grace Church Munyaka - Running Update")
print("=" * 50)

print("\n0. Pulling latest changes...")
os.system("git fetch origin")
os.system("git reset --hard origin/main")

# Ensure static files and media are reachable from public_html (cPanel file-based)
for helper in ('setup_media.py', 'link_media.py'):
    if os.path.exists(helper):
        os.system(sys.executable + ' ' + helper)

print("\n1. Running migrations...")
import django
django.setup()
from django.core.management import call_command
call_command('migrate')
print("   Migrations completed!")

print("\n2. Collecting static files...")
call_command('collectstatic', '--noinput')
print("   Static files collected!")

restart = os.path.join(BASE_DIR, 'tmp', 'restart.txt')
os.makedirs(os.path.dirname(restart), exist_ok=True)
with open(restart, 'w') as f:
    f.write('')
print("\n3. Passenger/App restart triggered (tmp/restart.txt + setup_media.py).")

# Link media + static into public_html (file-based, no terminal needed)
for helper in ('setup_media.py', 'link_media.py'):
    helper_path = os.path.join(BASE_DIR, helper)
    if os.path.exists(helper_path):
        print(f"\n4. Running {helper} ...")
        os.system(f'"{sys.executable}" "{helper_path}"')

print("\n" + "=" * 50)
print("UPDATE COMPLETED SUCCESSFULLY!")
print("=" * 50)
