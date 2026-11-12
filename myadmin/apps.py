from django.apps import AppConfig
from django.db import DEFAULT_DB_ALIAS
from django.db.models.signals import post_migrate


class MyadminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myadmin'

    def ready(self):
        post_migrate.connect(sync_permissions, sender=self)


def sync_permissions(apps, using=DEFAULT_DB_ALIAS, **kwargs):
    """
    Copy the permission catalogue into the `permissions` table after every `migrate`, adding new keys and updating
    descriptions. Django creates its own permissions the same way. Keys removed from the catalogue are left in the table.
    """
    from common.permissions import PERMISSIONS

    try:
        permission = apps.get_model('myadmin', 'Permission')
    except LookupError:  # myadmin's migrations were just reversed, so the table doesn't exist
        return
    permission.objects.using(using).bulk_create(
        [permission(key=key, description=description) for key, description in PERMISSIONS.items()],
        update_conflicts=True, unique_fields=['key'], update_fields=['description'],
    )
