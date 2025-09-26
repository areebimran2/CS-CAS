from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.functions import RandomUUID
from django.contrib.postgres.fields import CIEmailField
from django.utils.translation import gettext_lazy as _

from common.enums import UserStatus
from common.fields import PostgresEnumField
from common.functions import TxNow
from common.triggers import set_updated_at_trg

from phonenumber_field.modelfields import PhoneNumberField

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

    # role->permission
    permissions = models.ManyToManyField(Permission, related_name='role_permissions', through='RolePermission')

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

class User(AbstractUser):
    # AbstractUser fields that are not used
    username = None
    last_login = None
    is_active = None
    date_joined = None

    id = models.UUIDField(primary_key=True, db_default=RandomUUID())

    # Note that CIEmailField uses citext type which is no longer maintained in favor of case-insensitive collation
    email = models.EmailField(db_collation='case_insensitive', null=False)

    # Store phone numbers in E.164 format
    phone = PhoneNumberField(null=False)

    # Keep password as a VARCHAR(128) as hashed passwords are typically fall under such length
    password = models.CharField(max_length=128, null=False, db_column='password_hash')

    twofa_enabled = models.BooleanField(db_default=True, null=False)
    twofa_method = models.TextField(db_default='sms', choices=[('sms', 'SMS'), ('totp', 'TOTP')], null=True)
    status = PostgresEnumField('user_status', db_default=UserStatus.ACTIVE, choices=UserStatus.choices, null=False)
    designation = models.TextField(null=True)
    first_name = models.TextField(null=False)
    middle_name = models.TextField(null=True)
    last_name = models.TextField(null=False)
    created_at = models.DateTimeField(db_default=TxNow(), null=False)
    updated_at = models.DateTimeField(db_default=TxNow(), null=False)

    # Django specific fields for Django admin control
    is_superuser = models.BooleanField(
        _("superuser status"),
        default=False,
        help_text=_(
            "Designates that this user has all permissions without "
            "explicitly assigning them."
        ),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    roles = models.ManyToManyField(Role, related_name='user_roles', through='UserRole')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        constraints = [
            models.UniqueConstraint(
                fields=['phone'],
                name='users_phone_key',
            ),
            models.UniqueConstraint(
                fields=['email'],
                name='users_email_key',
            ),
            models.CheckConstraint(
                check=models.Q(twofa_method__in=['sms','totp']),
                name='users_twofa_method_check',
            )
        ]
        triggers = [
            set_updated_at_trg('trg_users_updated'),
        ]

    @property
    def is_active(self):
        return self.status == UserStatus.ACTIVE

    @is_active.setter
    def is_active(self, value):
        if value:
            self.status = UserStatus.ACTIVE
        else:
            self.status = UserStatus.SUSPENDED

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_index=False)
    pk = models.CompositePrimaryKey('user_id', 'role_id')

    class Meta:
        db_table = 'user_roles'