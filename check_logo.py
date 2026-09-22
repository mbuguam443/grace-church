#!/usr/bin/env python
"""Check logo settings and file paths."""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbms.settings_production')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from core.models import ChurchSetting
from django.conf import settings

print("=" * 50)
print("Logo Debug Info")
print("=" * 50)

# Check settings
print(f"\nMEDIA_URL: {settings.MEDIA_URL}")
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"MEDIA_ROOT exists: {os.path.exists(str(settings.MEDIA_ROOT))}")

# Check ChurchSetting
cs = ChurchSetting.get_settings()
print(f"\nChurch Setting (pk={cs.pk}):")
print(f"  church_name: {cs.church_name}")
print(f"  short_name: {cs.short_name}")
print(f"  logo: {cs.logo}")
print(f"  logo.url: {cs.logo.url if cs.logo else 'NO LOGO'}")
print(f"  favicon: {cs.favicon}")

# Check if logo file exists
if cs.logo:
    logo_path = os.path.join(str(settings.MEDIA_ROOT), str(cs.logo))
    print(f"\n  Logo file path: {logo_path}")
    print(f"  Logo file exists: {os.path.exists(logo_path)}")

# List media directory
media_dir = str(settings.MEDIA_ROOT)
if os.path.exists(media_dir):
    print(f"\nMedia directory contents:")
    for root, dirs, files in os.walk(media_dir):
        for f in files:
            filepath = os.path.join(root, f)
            print(f"  {filepath}")
else:
    print(f"\nMedia directory does not exist: {media_dir}")

# Check public_html symlink
public_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public_html')
symlink_path = os.path.join(public_dir, 'media')
print(f"\npublic_html dir: {public_dir}")
print(f"public_html exists: {os.path.exists(public_dir)}")
print(f"media symlink: {symlink_path}")
print(f"media symlink exists: {os.path.exists(symlink_path)}")
print(f"media symlink is link: {os.path.islink(symlink_path)}")

print("\n" + "=" * 50)
