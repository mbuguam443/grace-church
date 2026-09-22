#!/usr/bin/env python
"""
Setup media file serving on cPanel.
Run this once after setup.py to create a symlink for media files.
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbms.settings_production')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.conf import settings

media_root = str(settings.MEDIA_ROOT)
public_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public_html')

# Create public_html if it doesn't exist
if not os.path.exists(public_dir):
    os.makedirs(public_dir)
    print(f"Created: {public_dir}")

# Create symlink for media
symlink_path = os.path.join(public_dir, 'media')
if os.path.islink(symlink_path):
    os.unlink(symlink_path)
    print(f"Removed existing symlink: {symlink_path}")

if not os.path.exists(symlink_path):
    os.symlink(media_root, symlink_path)
    print(f"Created symlink: {symlink_path} -> {media_root}")
else:
    print(f"Media path already exists: {symlink_path}")

print("\nMedia serving configured!")
print(f"Uploads will be accessible at: /media/")
