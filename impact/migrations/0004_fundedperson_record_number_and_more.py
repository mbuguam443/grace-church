import django.utils.timezone
from django.db import migrations, models


def backfill_record_numbers(apps, schema_editor):
    FundedPerson = apps.get_model('impact', 'FundedPerson')
    for index, person in enumerate(FundedPerson.objects.order_by('id'), start=1):
        if not person.record_number:
            person.record_number = "OF-%05d" % index
            person.save(update_fields=['record_number'])


class Migration(migrations.Migration):

    dependencies = [
        ('impact', '0003_fundedperson_age_fundedperson_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundedperson',
            name='record_number',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='fundedperson',
            name='date_helped',
            field=models.DateField(default=django.utils.timezone.localdate, verbose_name='Date Admitted'),
        ),
        migrations.RunPython(backfill_record_numbers, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='fundedperson',
            name='record_number',
            field=models.CharField(blank=True, max_length=20, unique=True),
        ),
    ]
