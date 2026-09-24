from django.db import migrations

from core.about_defaults import ABOUT_DIVINE_PROMISE

OLD_ABOUT_DIVINE_PROMISE = (
    "Based on Revelation 3:8, Grace Church believes God has set before it an open door "
    "that no one can shut. This promise strengthens its mission of evangelism, community "
    "service, and faithful proclamation of the Gospel."
)


def forwards(apps, schema_editor):
    ChurchSetting = apps.get_model('core', 'ChurchSetting')
    for obj in ChurchSetting.objects.all():
        if obj.about_divine_promise in (None, '', OLD_ABOUT_DIVINE_PROMISE):
            obj.about_divine_promise = ABOUT_DIVINE_PROMISE
            obj.save(update_fields=['about_divine_promise'])


def backwards(apps, schema_editor):
    ChurchSetting = apps.get_model('core', 'ChurchSetting')
    for obj in ChurchSetting.objects.all():
        if obj.about_divine_promise == ABOUT_DIVINE_PROMISE:
            obj.about_divine_promise = OLD_ABOUT_DIVINE_PROMISE
            obj.save(update_fields=['about_divine_promise'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_update_about_call'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]