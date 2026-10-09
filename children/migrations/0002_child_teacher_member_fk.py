import django.db.models.deletion
from django.db import migrations, models


def match_teachers_to_members(apps, schema_editor):
    """Best-effort: link previously typed teacher names to member records."""
    Child = apps.get_model('children', 'Child')
    Member = apps.get_model('members', 'Member')
    members = list(Member.objects.all())
    for child in Child.objects.exclude(teacher_name='').exclude(teacher_name__isnull=True):
        text = (child.teacher_name or '').strip().lower()
        if not text:
            continue
        for member in members:
            full = f"{member.first_name} {member.last_name}".strip().lower()
            if text == full or text in full or full in text:
                child.teacher_id = member.pk
                child.save(update_fields=['teacher'])
                break


class Migration(migrations.Migration):

    dependencies = [
        ('children', '0001_initial'),
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='child',
            old_name='teacher',
            new_name='teacher_name',
        ),
        migrations.AddField(
            model_name='child',
            name='teacher',
            field=models.ForeignKey(
                blank=True,
                help_text='Sunday school teacher, chosen from the member list.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='children_taught',
                to='members.member',
            ),
        ),
        migrations.RunPython(match_teachers_to_members, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='child',
            name='teacher_name',
        ),
    ]
