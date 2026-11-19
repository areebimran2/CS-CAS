from typing import Optional

from ninja import Schema
from pydantic import Field

from common.enums import DashboardWidget, FXMode


class WidgetPlacement(Schema):
    """Where one widget sits on the dashboard grid."""
    widget: DashboardWidget
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    width: int = Field(ge=1)
    height: int = Field(ge=1)


class DashboardLayout(Schema):
    """The signed-in user's dashboard (spec M2). Used for both the request and the response."""
    widgets: list[WidgetPlacement]
    fx_mode: FXMode = FXMode.MANUAL
    default_date_range_days: Optional[int] = Field(default=None, ge=1, description='How far ahead lists look')
