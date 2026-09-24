from django.db import migrations

SEED_LEADERS = [
    {
        'name': 'Pastor John Mbugua',
        'role': 'Senior Pastor',
        'bio': 'Founding pastor and visionary leader of FBMI Church since 1995, whose leadership Grace Church Munyaka continues.',
    },
    {
        'name': 'Rev. Mary Mbugua',
        'role': 'Co-Pastor',
        'bio': "Co-founder and lead pastor of the Women's Ministry.",
    },
    {
        'name': 'Rev. Sarah Kimani',
        'role': 'Associate Pastor',
        'bio': 'Leads discipleship and spiritual formation programs.',
    },
    {
        'name': 'Pastor David Ochieng',
        'role': 'Youth Pastor',
        'bio': "Passionate about raising the next generation of God's leaders.",
    },
]


def forwards(apps, schema_editor):
    Leader = apps.get_model('core', 'Leader')
    existing = set(Leader.objects.values_list('name', flat=True))
    for i, item in enumerate(SEED_LEADERS):
        if item['name'] not in existing:
            Leader.objects.create(order=i + 1, **item)


def backwards(apps, schema_editor):
    Leader = apps.get_model('core', 'Leader')
    Leader.objects.filter(name__in=[item['name'] for item in SEED_LEADERS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_leader'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]