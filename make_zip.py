"""Build the deployable zip of the church site.

Excludes the things a server does not need and that would bloat or leak the
package: git history, virtualenvs, caches, node_modules and Expo build output.
Entry names always use forward slashes so the archive extracts correctly on
Linux (PowerShell's Compress-Archive and .NET's ZipFile both emit backslashes
on Windows, which unzip and cPanel mishandle).
"""

import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(ROOT), os.path.basename(ROOT) + '.zip'
)

EXCLUDE_DIRS = {
    '.git', 'venv', '.venv', 'env', '__pycache__', 'node_modules',
    '.expo', '.idea', '.vscode', 'staticfiles', '.pytest_cache',
    'dist', 'web-build',
}
EXCLUDE_SUFFIXES = ('.pyc', '.pyo', '.log', '.orig', '.rej')
EXCLUDE_NAMES = {'cpanel error.txt', '.DS_Store'}


def keep(rel_path, is_dir):
    parts = rel_path.split(os.sep)
    if any(p in EXCLUDE_DIRS for p in parts[:-1]):
        return False
    name = parts[-1]
    if name in EXCLUDE_DIRS:
        return not is_dir
    if name in EXCLUDE_NAMES or name.endswith(EXCLUDE_SUFFIXES):
        return False
    return True


def main():
    if os.path.exists(OUT):
        os.remove(OUT)
    count = 0
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            rel_dir = os.path.relpath(dirpath, ROOT)
            dirnames[:] = [d for d in dirnames if keep(os.path.join(rel_dir, d), True)]
            for name in filenames:
                rel = os.path.normpath(os.path.join(rel_dir, name))
                if not keep(rel, False):
                    continue
                zf.write(os.path.join(dirpath, name), rel.replace(os.sep, '/'))
                count += 1
    print('wrote %s (%d files, %.1f MB)' % (OUT, count, os.path.getsize(OUT) / 1048576))


if __name__ == '__main__':
    main()
