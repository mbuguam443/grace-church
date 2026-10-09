import django.db.models.deletion
from django.db import migrations, models


def match_teachers_to_members(apps, schema_editor):
    """Best-effort: link previously typed teacher names to member records."""
    BibleStudyNote = apps.get_model('bible_study', 'BibleStudyNote')
    Member = apps.get_model('members', 'Member')
    members = list(Member.objects.all())
    for study in BibleStudyNote.objects.exclude(teacher_name='').exclude(teacher_name__isnull=True):
        text = (study.teacher_name or '').strip().lower()
        if not text:
            continue
        for member in members:
            full = f"{member.first_name} {member.last_name}".strip().lower()
            if text == full or text in full or full in text:
                study.teacher_id = member.pk
                study.save(update_fields=['teacher'])
                break


class Migration(migrations.Migration):

    dependencies = [
        ('bible_study', '0006_biblestudynote_enable_registration_and_more'),
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='biblestudynote',
            old_name='teacher',
            new_name='teacher_name',
        ),
        migrations.AddField(
            model_name='biblestudynote',
            name='teacher',
            field=models.ForeignKey(
                blank=True,
                help_text='Teacher, chosen from the member list.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='bible_studies_taught',
                to='members.member',
            ),
        ),
        migrations.RunPython(match_teachers_to_members, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='biblestudynote',
            name='teacher_name',
        ),
    ]
