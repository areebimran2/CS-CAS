from ninja import ModelSchema

from myadmin.models import Permission


class PermissionOut(ModelSchema):
    class Meta:
        model = Permission
        fields = ['key', 'description']

