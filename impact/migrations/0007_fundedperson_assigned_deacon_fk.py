import django.db.models.deletion
from django.db import migrations, models


def match_deacons_to_members(apps, schema_editor):
    """Best-effort: link previously typed deacon names to member records."""
    FundedPerson = apps.get_model('impact', 'FundedPerson')
    Member = apps.get_model('members', 'Member')
    members = list(Member.objects.all())
    for person in FundedPerson.objects.exclude(assigned_deacon_name='').exclude(assigned_deacon_name__isnull=True):
        text = (person.assigned_deacon_name or '').strip().lower()
        if not text:
            continue
        for member in members:
            full = f"{member.first_name} {member.last_name}".strip().lower()
            if text == full or text in full or full in text:
                person.assigned_deacon_id = member.pk
                person.save(update_fields=['assigned_deacon'])
                break


class Migration(migrations.Migration):

    dependencies = [
        ('impact', '0006_fundedperson_assigned_deacon'),
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fundedperson',
            old_name='assigned_deacon',
            new_name='assigned_deacon_name',
        ),
        migrations.AddField(
            model_name='fundedperson',
            name='assigned_deacon',
            field=models.ForeignKey(
                blank=True,
                help_text='Deacon or deaconess assigned for follow-up, prayer and discipleship.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='assigned_funded_people',
                to='members.member',
            ),
        ),
        migrations.RunPython(match_deacons_to_members, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='fundedperson',
            name='assigned_deacon_name',
        ),
    ]
