# Grace Church Munyaka Management System

A complete, production-ready Church Management System for **Grace Church Munyaka (GC)** built with Django.

## Features

### Core Modules
- **Dashboard** - Real-time statistics, charts, and quick access
- **Members** - Complete member management with profiles, search, and history
- **Families** - Family/household management with relationships
- **Visitors** - Visitor tracking and follow-up management
- **Services** - Service scheduling and management
- **Attendance** - Attendance tracking for members, visitors, and children
- **Ministries** - Ministry/department management
- **Groups** - Small group/cell group management
- **Events** - Event management with registration
- **Finance** - Income and expense tracking
- **Giving** - Member giving/tithe records
- **Prayer Requests** - Prayer request submission and management
- **Sermons** - Sermon library with media support
- **Children** - Children's ministry with check-in/check-out
- **Communication** - Announcements and notifications
- **Assets** - Church asset inventory
- **Facilities** - Room/facility booking
- **Reports** - Comprehensive reporting with filters

### User Roles
- Super Admin, Admin, Pastor, Secretary, Finance Officer
- Ministry Leader, Group Leader, Media, Usher, Member

### Additional Features
- Public-facing church website
- Member portal
- Role-based access control
- Responsive design (desktop, tablet, mobile)
- Custom admin dashboard (not Django admin)
- M-Pesa integration ready
- Sample data seeding

## Requirements

- Python 3.10+
- Django 4.2+

## Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd fbms
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Seed demo data (optional):
```bash
python manage.py seed_data
```

8. Run the development server:
```bash
python manage.py runserver
```

## Default Credentials

After seeding:
- **Super Admin:** `admin` / `admin123`
- **Pastor:** `pastor` / `demo123`
- **Secretary:** `secretary` / `demo123`
- **Finance:** `finance` / `demo123`
- **Ministry Leader:** `ministry_leader` / `demo123`
- **Group Leader:** `group_leader` / `demo123`

## M-Pesa Configuration

Set these environment variables in `.env`:
```
MPESA_CONSUMER_KEY=your_key
MPESA_CONSUMER_SECRET=your_secret
MPESA_SHORTCODE=your_shortcode
MPESA_PASSKEY=your_passkey
MPESA_ENV=sandbox
```

## Database

SQLite is used by default. To switch to PostgreSQL, update the `DATABASES` setting in `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fbms_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Running Tests

```bash
python manage.py test
```

## Project Structure

```
fbms/
├── accounts/        # Authentication & user management
├── assets/          # Church asset management
├── attendance/      # Attendance tracking
├── children/        # Children's ministry
├── communication/   # Announcements
├── core/            # Settings, notifications, seed data
├── dashboard/       # Admin dashboard
├── events/          # Event management
├── facilities/      # Facility booking
├── families/        # Family management
├── finance/         # Financial management
├── giving/          # Giving/tithe records
├── groups/          # Small groups
├── members/         # Member management
├── ministries/      # Ministry management
├── prayer/          # Prayer requests
├── public/          # Public website
├── reports/         # Reports
├── sermons/         # Sermon management
├── services/        # Church services
├── visitors/        # Visitor management
├── templates/       # Django templates
├── static/          # CSS, JS, images
├── fbms/            # Project settings
├── manage.py
├── requirements.txt
└── README.md
```

## Deployment Notes

1. Set `DEBUG = False` in production
2. Set a strong `SECRET_KEY`
3. Configure `ALLOWED_HOSTS`
4. Use PostgreSQL in production
5. Set up proper static file serving (Whitenoise or CDN)
6. Use HTTPS
7. Configure email backend for notifications
8. Set up regular database backups

## License

Proprietary - Grace Church Munyaka
