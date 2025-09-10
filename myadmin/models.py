from django.db import models

# from django.contrib.postgres.functions import RandomUUID
# from django.utils import timezone
#
#
# class Permission(models.Model):
#     key = models.TextField(primary_key=True)
#     description = models.TextField()
#
# class Role(models.Model):
#     id = models.UUIDField(primary_key=True, default=RandomUUID)
#     name = models.TextField(unique=True, null=False)
#     description = models.TextField()
#     created_at = models.DateTimeField(default=timezone.now, null=False)
#     updated_at = models.DateTimeField(default=timezone.now, null=False)
#
#     # role->permission
#     permissions = models.ManyToManyField(Permission, related_name='role_permission')
