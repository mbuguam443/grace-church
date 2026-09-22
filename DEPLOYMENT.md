# Grace Church Munyaka Management System - cPanel Deployment Guide

## Prerequisites
- cPanel account with Python support
- SSH access (recommended)
- Domain name pointed to your hosting

## Step 1: Prepare Your Project

### 1.1 Update settings_production.py
Edit `fbms/settings_production.py`:
- Set a strong `SECRET_KEY`
- Add your domain to `ALLOWED_HOSTS`
- Configure database settings (if using PostgreSQL)

### 1.2 Generate a Secure Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Step 2: Upload Files to cPanel

### Option A: Via File Manager
1. Log in to cPanel
2. Open File Manager
3. Navigate to your domain's root folder (usually `public_html`)
4. Upload all project files

### Option B: Via FTP/SFTP
Use an FTP client (FileZilla, WinSCP) to upload files to your domain root

### Option C: Via Git (if available)
```bash
git clone <your-repo-url> .
```

## Step 3: Set Up Python Application in cPanel

1. Log in to cPanel
2. Go to **Setup Python App** (or **Python Selector**)
3. Click **Create Application**
4. Select Python version (3.9+ recommended)
5. Set the application root to your project folder
6. Set the application URL (your domain)
7. Set the application startup file to `passenger_wsgi.py`
8. Click **Create**

## Step 4: Install Dependencies

### Via SSH (recommended)
```bash
cd ~/your-project-folder
source ~/virtualenv/your-project/3.9/bin/activate
pip install -r requirements.txt
```

### Via cPanel Terminal
1. Open **Terminal** in cPanel
2. Navigate to your project folder
3. Run the pip install command

## Step 5: Configure Environment Variables

In cPanel's Python App settings, add these environment variables:
```
DJANGO_SECRET_KEY=your-secure-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
TIME_ZONE=Africa/Nairobi
```

Or create a `.env` file in your project root:
```
DJANGO_SECRET_KEY=your-secure-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
TIME_ZONE=Africa/Nairobi
```

## Step 6: Run Migrations and Setup

### Via SSH
```bash
cd ~/your-project-folder
source ~/virtualenv/your-project/3.9/bin/activate
python manage.py migrate --settings=fbms.settings_production
python manage.py collectstatic --noinput --settings=fbms.settings_production
python manage.py createsuperuser --settings=fbms.settings_production
python manage.py seed_data --settings=fbms.settings_production
```

## Step 7: Configure Static Files

### Option A: Using Whitenoise (recommended)
Add to `MIDDLEWARE` in `settings_production.py`:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    ...
]
```

Add to `settings_production.py`:
```python
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Option B: Via cPanel
1. Copy files from `staticfiles/` to `public_html/static/`
2. Or configure an alias in cPanel

## Step 8: Configure .htaccess

The `.htaccess` file is already included. Make sure mod_rewrite is enabled on your server.

## Step 9: Restart Application

In cPanel's Python App section, click **Restart** to apply changes.

## Step 10: Test Your Website

1. Visit your domain
2. Test login functionality
3. Check all pages load correctly
4. Verify static files (CSS, JS, images) are loading

## Default Login Credentials
After seeding data:
- **Super Admin:** `admin` / `admin123`
- **Pastor:** `pastor` / `demo123`
- **Member:** `member1` / `test123`

## Troubleshooting

### 500 Internal Server Error
1. Check error logs in cPanel
2. Verify `SECRET_KEY` is set
3. Check file permissions (644 for files, 755 for folders)
4. Ensure `DEBUG = False` in production

### Static Files Not Loading
1. Run `python manage.py collectstatic`
2. Check `STATIC_ROOT` path
3. Verify `.htaccess` is configured

### Database Errors
1. Run `python manage.py migrate`
2. Check database file permissions
3. Verify SQLite is supported

### Import Errors
1. Ensure all dependencies are installed
2. Check Python version compatibility
3. Verify virtual environment is activated

## Security Checklist
- [ ] Changed default `SECRET_KEY`
- [ ] Set `DEBUG = False`
- [ ] Added domain to `ALLOWED_HOSTS`
- [ ] Changed default admin password
- [ ] Enabled HTTPS (SSL certificate)
- [ ] Configured secure headers
- [ ] Set up regular backups

## Optional: PostgreSQL Database

If your cPanel supports PostgreSQL:

1. Create a database in cPanel > PostgreSQL Databases
2. Update `settings_production.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Support
For issues, check:
1. cPanel error logs
2. Django debug logs
3. Browser console (F12)
