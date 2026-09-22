from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_rolemodulepermission'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='kind',
            field=models.CharField(blank=True, max_length=40),
        ),
    ]
