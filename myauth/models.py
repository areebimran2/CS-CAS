from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.functions import RandomUUID
from django.utils.translation import gettext_lazy as _

from common.enums import UserStatus
from common.fields import PostgresEnumField
from common.functions import TxNow
from common.triggers import set_updated_at_trg

from phonenumber_field.modelfields import PhoneNumberField

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        UserPreference.objects.create(user=user)

        return user

    create_user.alters_data = True

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

    create_superuser.alters_data = True

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

    # Many-to-many role→permission
    permissions = models.ManyToManyField(Permission, related_name='roles', through='RolePermission')

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

class User(AbstractBaseUser, PermissionsMixin):
    # AbstractBaseUser fields that are not used
    last_login = None

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

    # Many-to-many user→role
    roles = models.ManyToManyField(Role, related_name='users', through='UserRole')

    # Django specific fields for Django admin control
    is_superuser = models.BooleanField(
        _("superuser status"),
        default=False,
        db_default=False,
        help_text=_(
            "Designates that this user has all permissions without "
            "explicitly assigning them."
        ),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        db_default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    objects = UserManager()

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

class UserPreference(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name='preferences')
    fx_mode = models.TextField(db_default='manual', choices=[('manual', 'Manual'), ('live', 'Live')], null=False)
    opt_in_enabled = models.BooleanField(db_default=False, null=False)
    notify_cabin_avail = models.BooleanField(db_default=True, null=False)
    notify_flash_sale = models.BooleanField(db_default=True, null=False)
    notify_release_request = models.BooleanField(db_default=True, null=False)

    class Meta:
        db_table = 'user_prefs'
        constraints = [
            models.CheckConstraint(
                check=models.Q(fx_mode__in=['manual', 'live']),
                name='user_prefs_fx_mode_check',
            )
        ]

class UserRole(models.Model):
    user = models.ForeignKey('myauth.User', on_delete=models.CASCADE, db_index=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_index=False)
    pk = models.CompositePrimaryKey('user_id', 'role_id')

    class Meta:
        db_table = 'user_roles'

class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_index=False)
    perm_key = models.ForeignKey(Permission, on_delete=models.CASCADE, db_column='perm_key', db_index=False)
    pk = models.CompositePrimaryKey('role_id', 'perm_key')

    class Meta:
        db_table = 'role_permissions'