# Grace Church Munyaka Management System — cPanel File-Based Deployment

Target site: **http://gracechurch.schones-heim-builders.co.ke**
Database: **MySQL (phpMyAdmin)** via **PyMySQL** (`pymysql.install_as_MySQLdb()` in `fbms/settings_production.py`).

This guide is **file-based only** — every step is done in the cPanel browser UI. No SSH, no terminal, no command line.

## Prerequisites
- cPanel account
- Subdomain `gracechurch` created (→ `gracechurch.schones-heim-builders.co.ke`)
- MySQL database created in cPanel (phpMyAdmin)

## Step 1: Create the MySQL database (cPanel → MySQL® Databases)
1. Create database: `wlsihszp_gracechurch`
2. Create user: `wlsihszp_gracechurch`, password `Me32323383#&`
3. Add user to database → **ALL PRIVILEGES**

Already done in `fbms/settings_production.py` defaults — no code change needed unless your names differ.

## Step 2: Prepare the database (skip schema import)
No SQL file is needed — the `migrate` step (Step 7) creates every table in MySQL automatically.
If you ever want a database backup, use **cPanel → phpMyAdmin → Export** on `wlsihszp_gracechurch`.

> Note: Django's `dumpdata` exports *data* (JSON/XML/YAML), not schema — there is no `--format=sql`. To produce a plain `schema.sql` yourself, run `migrate` locally against a scratch DB, then export from phpMyAdmin/MySQL.

## Step 3: Upload the app (cPanel → File Manager)
1. Open File Manager → go to the **subdomain root** (e.g. `public_html/gracechurch` or the docroot for the subdomain)
2. Upload the project zip, right-click → **Extract**
3. Confirm these exist: `passenger_wsgi.py`, `manage.py`, `setup.php`, `manage.php`, `requirements.txt`, `.env`

## Step 4: Create the Python app (cPanel → Setup Python App)
1. **Setup Python App** → **Create Application**
2. Application root: the folder you uploaded to (e.g. `~/gc` or your subdomain docroot)
3. Application URL: `http://gracechurch.schones-heim-builders.co.ke`
4. Application startup file: `passenger_wsgi.py`
5. Python version: 3.10+ (whatever cPanel offers ≥3.10)
6. Click **Create** — cPanel creates a virtualenv for you

## Step 5: Install dependencies (no terminal!)
In the **Setup Python App** screen for your app:
1. Open the app → **Manage requirements** (or the requirements.txt box)
2. Confirm `requirements.txt` contents are listed (django, PyMySQL, whitenoise, Pillow, python-dotenv, gunicorn)
3. Save — cPanel runs `pip install -r requirements.txt` inside the virtualenv for you

## Step 6: Environment variables (no .env edit needed if you use Setup Python App)
In **Setup Python App → your app → Environment Variables**, add:
```
DJANGO_SECRET_KEY=<generate a long random string>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=gracechurch.schones-heim-builders.co.ke
DB_NAME=wlsihszp_gracechurch
DB_USER=wlsihszp_gracechurch
DB_PASSWORD=Me32323383#&
DB_HOST=localhost
DB_PORT=3306
TIME_ZONE=Africa/Nairobi
CHURCH_NAME=Grace Church Munyaka
CHURCH_SHORT_NAME=GC
```
Alternatively create a `.env` in the app root with the same keys (`settings.py` uses `python-dotenv`; `settings_production.py` reads `os.environ`, so prefer the Setup Python App env vars for production).

## Step 7: Start the app — first start auto-syncs the database
`passenger_wsgi.py` runs `migrate` + `collectstatic` automatically on the **first** app start (writes a `.dbsynced` marker so it only runs once). So after creating the Python app and installing requirements, just **Restart** it (Step 9) and the tables are created in MySQL.

> Why not `setup.php`? When a Python app is created at the subdomain **root**, Passenger serves *every* request to Django, so `.php` files in the app root are not reachable (they return 404). The auto-migrate startup replaces the PHP "Run All Setup" flow for this layout.
>
> `setup.php` / `manage.php` are still valid if you instead create the Python app under a sub-path (e.g. app URL `/gc` at app root `~/gc`) and keep the PHP helpers in the subdomain document root outside it.

Check the sync result anytime: open `startup.log` in File Manager. If the first start failed (e.g. wrong DB password), it says so there and retries on every restart until `.dbsynced` exists.

## Step 8: Media uploads
First-start sync does not need media setup — `media/` is created automatically when anything is uploaded.
Serving uploads publicly at `/media/` while the app sits at the Passenger root needs a small Django media URL (not covered here); until then, uploads work inside the admin/dashboard (Django stores them, whitenoise serves only `/static/`).

## Step 9: Restart the app
cPanel → **Setup Python App** → your app → **Restart**

## Step 10: Test
1. Visit `http://gracechurch.schones-heim-builders.co.ke`
2. Log in at `/accounts/login/` → dashboard at `/dashboard/`
3. Check static files load (CSS/JS/images)

## Updating later (still no terminal)
1. Upload a new zip via File Manager and extract (over the old files), **or**
2. Run `update.py` from a one-off Python run (Setup Python App → run script), which pulls git, migrates, collects static, and restarts Passenger via `tmp/restart.txt`

## Default login credentials
After seeding:
- **Super Admin:** `admin` / `admin123`
- **Pastor:** `pastor` / `demo123`
- **Member:** `member1` / `test123`

## Troubleshooting
### 500 Internal Server Error
1. cPanel → Error Logs (or `logs/` folder)
2. Verify env vars in Setup Python App (SECRET_KEY, DB_*)
3. File permissions: 644 for files, 755 for folders
4. `DEBUG = False` in production (already set)

### Static files not loading
1. Re-run `setup.php?action=collectstatic`
2. Whitenoise is already in `MIDDLEWARE` — static is served by Django, no Apache alias required
3. If you prefer Apache: remove the `Alias` placeholder in `.htaccess` and point it at your real app path

### Database errors
1. Re-run `setup.php?action=migrate`
2. Confirm DB name/user/password in Setup Python App env vars match Step 1
3. Confirm the user has ALL PRIVILEGES on the database

### "An error occurred during installation of modules" (content-type mismatch on check)
Common cPanel false positive. The modules DID install ("the operation was performed"). The availability check compares the homepage before/after pip install (`text/html` vs `text/html; charset=utf-8`) — a harmless string mismatch, or the homepage 500s because `migrate` hasn't run yet.
Fix: open `startup.log` (see Step 7) and verify `.dbsynced` exists, then **Restart** the app from Setup Python App and reload the homepage. Once it returns 200 the error can be ignored.

### `python`/`python3` not found from setup.php
The scripts fall back through `venv/bin/python` → `$VIRTUAL_ENV/bin/python` → `python3` → `python`. If all fail, set the `VIRTUAL_ENV` environment variable in Setup Python App to your virtualenv path.

## Security checklist
- [ ] `SECRET_KEY` set to a long random value
- [ ] `DEBUG = False`
- [ ] `DJANGO_ALLOWED_HOSTS` contains only your domain
- [ ] Default admin password changed
- [ ] HTTPS/SSL enabled for the subdomain
- [ ] `.env` (if used) is not publicly reachable (it is git-ignored; confirm File Manager shows it outside the web root or has 600 perms)

## Support
Check: cPanel error logs, `logs/` folder, browser console (F12).
