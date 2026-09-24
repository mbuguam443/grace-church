from django.db import migrations

from core.about_defaults import ABOUT_CALL, ABOUT_DIVINE_PROMISE

OLD_ABOUT_CALL = (
    "To grow in the grace and knowledge of our Lord and Savior Jesus Christ (2 Peter 3:16). "
    "We are committed to nurturing spiritual maturity through God's Word, prayer, worship, "
    "fellowship, and faithful service. As we grow in Christ, we seek to reflect His love, "
    "share His Gospel, and bring glory to His name in all that we do."
)

OLD_ABOUT_DIVINE_PROMISE = (
    "An open door (Revelation 3:8). This divine promise gives us confidence to proclaim "
    "the Gospel, serve our community, and fulfill the mission He has entrusted to us."
)


def forwards(apps, schema_editor):
    ChurchSetting = apps.get_model('core', 'ChurchSetting')
    for obj in ChurchSetting.objects.all():
        changed = False
        if obj.about_call in (None, '', OLD_ABOUT_CALL):
            obj.about_call = ABOUT_CALL
            changed = True
        if obj.about_divine_promise in (None, '', OLD_ABOUT_DIVINE_PROMISE):
            obj.about_divine_promise = ABOUT_DIVINE_PROMISE
            changed = True
        if changed:
            obj.save(update_fields=['about_call', 'about_divine_promise'])


def backwards(apps, schema_editor):
    ChurchSetting = apps.get_model('core', 'ChurchSetting')
    for obj in ChurchSetting.objects.all():
        changed = False
        if obj.about_call == ABOUT_CALL:
            obj.about_call = OLD_ABOUT_CALL
            changed = True
        if obj.about_divine_promise == ABOUT_DIVINE_PROMISE:
            obj.about_divine_promise = OLD_ABOUT_DIVINE_PROMISE
            changed = True
        if changed:
            obj.save(update_fields=['about_call', 'about_divine_promise'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_update_about_divine_promise'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]