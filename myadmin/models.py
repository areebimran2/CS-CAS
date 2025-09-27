from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.functions import RandomUUID

from common.functions import TxNow
from common.triggers import set_updated_at_trg

class Permission(models.Model):
    key = models.TextField(primary_key=True)
    description = models.TextField(null=True)

    class Meta:
        db_table = 'permissions'

class Role(models.Model):
    id = models.UUIDField(primary_key=True, db_default=RandomUUID())
    name = models.TextField(null=False)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    # Note that many-to-many fields can be placed in either model of the relationship. The result is more or less
    # the same.
    # Many-to-many role→permission
    permissions = models.ManyToManyField(Permission, related_name='role_permissions', through='RolePermission')
    # Many-to-many user→role
    users = models.ManyToManyField('myauth.User', related_name='user_roles', through='UserRole')

    class Meta:
        db_table = 'roles'
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                name='roles_name_key'
            ),
        ]
        triggers = [
            set_updated_at_trg('trg_roles_updated'),
        ]

class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_index=False)
    perm_key = models.ForeignKey(Permission, on_delete=models.CASCADE, db_column='perm_key', db_index=False)
    pk = models.CompositePrimaryKey('role_id', 'perm_key')

    class Meta:
        db_table = 'role_permissions'

class UserRole(models.Model):
    user = models.ForeignKey('myauth.User', on_delete=models.CASCADE, db_index=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_index=False)
    pk = models.CompositePrimaryKey('user_id', 'role_id')

    class Meta:
        db_table = 'user_roles'