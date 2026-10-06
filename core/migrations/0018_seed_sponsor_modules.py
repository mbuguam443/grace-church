from django.db import migrations


def seed_sponsor_modules(apps, schema_editor):
    RoleModulePermission = apps.get_model('core', 'RoleModulePermission')
    RoleModulePermission.objects.get_or_create(role='sponsor', module='impact')


def unseed_sponsor_modules(apps, schema_editor):
    RoleModulePermission = apps.get_model('core', 'RoleModulePermission')
    RoleModulePermission.objects.filter(role='sponsor', module='impact').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_alter_rolemodulepermission_module_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_sponsor_modules, unseed_sponsor_modules),
    ]
