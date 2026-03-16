from django.contrib.auth import get_user_model
from ninja import Schema, ModelSchema

from typing import Optional

from myauth.models import UserPreference


class UserPrefSchema(ModelSchema):
    class Meta:
        model = UserPreference
        fields = ['opt_in_enabled', 'notify_cabin_avail', 'notify_flash_sale', 'notify_release_request', 'fx_mode']
        fields_optional = '__all__'

class UserProfileSchema(ModelSchema):
    preferences: UserPrefSchema

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'middle_name', 'last_name', 'designation',
                  'email', 'phone', 'twofa_method', 'twofa_enabled']
        fields_optional = ['middle_name']

    @staticmethod
    def resolve_phone(obj):
        return str(obj.phone)


class UserProfileUpdateSchema(Schema):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    designation: Optional[str] = None
    preferences: Optional[UserPrefSchema] = None

