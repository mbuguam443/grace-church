from django.db import migrations


def grant_impact_to_existing_roles(apps, schema_editor):
    """Roles saved before the Impact module existed never got the module row,
    so their sidebar silently hid Outreach. Give every existing role it."""
    RoleModulePermission = apps.get_model('core', 'RoleModulePermission')
    roles = RoleModulePermission.objects.values_list('role', flat=True).distinct()
    for role in roles:
        RoleModulePermission.objects.get_or_create(role=role, module='impact')


def revoke_impact_grants(apps, schema_editor):
    RoleModulePermission = apps.get_model('core', 'RoleModulePermission')
    RoleModulePermission.objects.filter(module='impact').exclude(role='sponsor').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_seed_sponsor_modules'),
    ]

    operations = [
        migrations.RunPython(grant_impact_to_existing_roles, revoke_impact_grants),
    ]
