#!/bin/bash
# Grace Church Munyaka Management System - cPanel Deployment Script

echo "=========================================="
echo "Grace Church Munyaka - cPanel Deployment Script"
echo "=========================================="

# Step 1: Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Step 2: Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=fbms.settings_production

# Step 3: Run migrations
echo "Running migrations..."
python manage.py migrate --settings=fbms.settings_production

# Step 4: Create superuser (optional)
echo "Create superuser? (y/n)"
read create_superuser
if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser --settings=fbms.settings_production
fi

# Step 5: Seed demo data (optional)
echo "Seed demo data? (y/n)"
read seed_data
if [ "$seed_data" = "y" ]; then
    python manage.py seed_data --settings=fbms.settings_production
fi

echo "=========================================="
echo "Deployment complete!"
echo "=========================================="
