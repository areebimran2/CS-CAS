from typing import Optional, List

from ninja import Schema, ModelSchema

from selling.models import ReserveSetting


class ReserveSettingsIn(Schema):
    max_hold_minutes: int
    reminder_scheduled_minutes: List[int]
    allow_extensions: Optional[bool] = None
    max_extensions: Optional[int] = None
    extension_minutes: Optional[int] = None


class ReserveSettingsOut(ModelSchema):
    class Meta:
        model = ReserveSetting
        fields = '__all__'
        exclude = ['created_at', 'created_by']

