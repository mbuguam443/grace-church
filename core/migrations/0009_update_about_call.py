from django.db import migrations

from core.about_defaults import ABOUT_CALL

OLD_ABOUT_CALL = (
    "To grow in the grace and knowledge of our Lord and Savior Jesus Christ. The church "
    "is committed to spiritual maturity through God's Word, prayer, worship, fellowship, "
    "and faithful service, bringing glory to Christ in all it does."
)


def forwards(apps, schema_editor):
    ChurchSetting = apps.get_model('core', 'ChurchSetting')
    for obj in ChurchSetting.objects.all():
        if obj.about_call in (None, '', OLD_ABOUT_CALL):
            obj.about_call = ABOUT_CALL
            obj.save(update_fields=['about_call'])


def backwards(apps, schema_editor):
    ChurchSetting = apps.get_model('core', 'ChurchSetting')
    for obj in ChurchSetting.objects.all():
        if obj.about_call == ABOUT_CALL:
            obj.about_call = OLD_ABOUT_CALL
            obj.save(update_fields=['about_call'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_update_about_history'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]