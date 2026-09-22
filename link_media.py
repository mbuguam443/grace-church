#!/usr/bin/env python
"""
Create symlink so media files are accessible via the browser.
Run this once on cPanel after setup.
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbms.settings_production')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.conf import settings

# Paths
project_dir = os.path.dirname(os.path.abspath(__file__))
media_root = str(settings.MEDIA_ROOT)
public_dir = os.path.join(os.path.dirname(project_dir), 'public_html')

print(f"Project dir: {project_dir}")
print(f"Media root: {media_root}")
print(f"Public dir: {public_dir}")

# Create public_html if needed
if not os.path.exists(public_dir):
    os.makedirs(public_dir)
    print(f"Created: {public_dir}")

# Create symlink
symlink_path = os.path.join(public_dir, 'media')
if os.path.islink(symlink_path):
    os.unlink(symlink_path)
    print(f"Removed old symlink")

try:
    os.symlink(media_root, symlink_path)
    print(f"Symlink created: {symlink_path} -> {media_root}")
    print("Media files are now accessible!")
except OSError as e:
    print(f"Symlink failed: {e}")
    print("\nAlternative: Copy media folder into public_html manually via File Manager")
