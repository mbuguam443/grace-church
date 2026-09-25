from django.db import migrations, models

from core.about_defaults import (
    FEATURED_EVENT_TITLE,
    FEATURED_EVENT_DESCRIPTION,
    FEATURED_EVENT_DATE,
    FEATURED_EVENT_TIME,
    FEATURED_EVENT_VENUE,
    FEATURED_EVENT_AUDIENCE,
)

BACKFILL = {
    'featured_event_title': FEATURED_EVENT_TITLE,
    'featured_event_description': FEATURED_EVENT_DESCRIPTION,
    'featured_event_date': FEATURED_EVENT_DATE,
    'featured_event_time': FEATURED_EVENT_TIME,
    'featured_event_venue': FEATURED_EVENT_VENUE,
}


def forwards(apps, schema_editor):
    ChurchSetting = apps.get_model('core', 'ChurchSetting')
    for obj in ChurchSetting.objects.all():
        changed = False
        for field, value in BACKFILL.items():
            current = getattr(obj, field, None)
            if current in (None, ''):
                setattr(obj, field, value)
                changed = True
        if obj.featured_event_audience in (None, ''):
            obj.featured_event_audience = FEATURED_EVENT_AUDIENCE
            changed = True
        if changed:
            obj.save(update_fields=list(BACKFILL) + ['featured_event_audience'])


def backwards(apps, schema_editor):
    ChurchSetting = apps.get_model('core', 'ChurchSetting')
    for obj in ChurchSetting.objects.all():
        changed = False
        for field, value in BACKFILL.items():
            if getattr(obj, field, None) == value:
                setattr(obj, field, '')
                changed = True
        if obj.featured_event_audience == FEATURED_EVENT_AUDIENCE:
            obj.featured_event_audience = ''
            changed = True
        if changed:
            obj.save(update_fields=list(BACKFILL) + ['featured_event_audience'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_seed_leaders'),
    ]

    operations = [
        migrations.AddField(
            model_name='churchsetting',
            name='featured_event_audience',
            field=models.CharField(blank=True, help_text='Featured event audience, e.g. Everyone.', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='churchsetting',
            name='featured_event_date',
            field=models.CharField(blank=True, help_text='Featured event date, e.g. Nov 11-15, 2024.', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='churchsetting',
            name='featured_event_description',
            field=models.TextField(blank=True, help_text='Featured event description on the Events page.', null=True),
        ),
        migrations.AddField(
            model_name='churchsetting',
            name='featured_event_image',
            field=models.ImageField(blank=True, help_text='Featured event image (leave blank for the default image).', null=True, upload_to='church/'),
        ),
        migrations.AddField(
            model_name='churchsetting',
            name='featured_event_link',
            field=models.URLField(blank=True, help_text='Optional button link (leave blank to use the contact page).', null=True),
        ),
        migrations.AddField(
            model_name='churchsetting',
            name='featured_event_time',
            field=models.CharField(blank=True, help_text='Featured event time, e.g. 6:00 PM - 9:00 PM.', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='churchsetting',
            name='featured_event_title',
            field=models.CharField(blank=True, help_text='Featured event title on the Events page.', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='churchsetting',
            name='featured_event_venue',
            field=models.CharField(blank=True, help_text='Featured event venue.', max_length=200, null=True),
        ),
        migrations.RunPython(forwards, backwards),
    ]