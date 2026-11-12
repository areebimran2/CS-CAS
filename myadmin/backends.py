from django.contrib.auth.backends import BaseBackend

from myadmin.models import Permission


class RolePermissionBackend(BaseBackend):
    """
    Grants each user the permissions of their roles, so Django's standard checks work with CS-CAS permissions:
    `user.has_perm('ships.edit')`. Active superusers have all permissions.
    """

    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or obj is not None:
            return set()
        # Cached on the user object, which is loaded once per request, so one query per request at most.
        if not hasattr(user_obj, '_role_perm_cache'):
            user_obj._role_perm_cache = set(
                Permission.objects.filter(role_permissions__users=user_obj).values_list('key', flat=True)
            )
        return user_obj._role_perm_cache
