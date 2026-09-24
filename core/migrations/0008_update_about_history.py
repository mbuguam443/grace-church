from django.db import migrations

from core.about_defaults import ABOUT_HISTORY_BODY

OLD_HISTORY_BODY = "\n\n".join([
    "In 2023, Harry and Alice Wamani purchased land in Zone-T, Ruiru East, Juja East, "
    "Kiambu County. They later acquired an adjoining plot, which Harry dedicated to the "
    "Lord as an offering of thanksgiving. That land would become the future home of Grace Church.",
    "After moving into their home in January 2025, Harry invited neighbours for what was "
    "meant to be a men's fellowship. Families came together instead, and it naturally became "
    "a weekly family fellowship centered on prayer, fellowship, and Bible study.",
    "As the fellowship grew, many residents desired a church within their community. After "
    "prayer and seeking another ministry to begin work in Zone-T, Harry became convinced that "
    "God was calling him to plant a church.",
    "On 22 June 2025, Harry and Alice met with Pastor Dr. Joseph Kinyanjui and his wife of "
    "FBMI Ruiru Church for prayer, counsel, and encouragement, marking the commissioning of "
    "the emerging ministry.",
    "The first official worship service was held on 29 June 2025. The inaugural sermon came "
    "from 2 Peter 3:18, and this verse inspired the name Grace Church.",
])


def forwards(apps, schema_editor):
    ChurchSetting = apps.get_model('core', 'ChurchSetting')
    for obj in ChurchSetting.objects.all():
        if obj.about_history_body in (None, '', OLD_HISTORY_BODY):
            obj.about_history_body = ABOUT_HISTORY_BODY
            obj.save(update_fields=['about_history_body'])


def backwards(apps, schema_editor):
    ChurchSetting = apps.get_model('core', 'ChurchSetting')
    for obj in ChurchSetting.objects.all():
        if obj.about_history_body == ABOUT_HISTORY_BODY:
            obj.about_history_body = OLD_HISTORY_BODY
            obj.save(update_fields=['about_history_body'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_churchsetting_about_call_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
