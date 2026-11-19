import uuid
from datetime import date
from typing import List, Optional

from ninja import Schema
from pydantic import Field
from pydantic_extra_types.currency_code import Currency

from common.enums import ExportDetail, FileFormat, FXMode


class ExportOptions(Schema):
    """The file to produce and the records it covers. Filters that don't apply to the module are ignored."""
    format: FileFormat = FileFormat.CSV
    detail: ExportDetail = ExportDetail.SUMMARY
    season_id: Optional[uuid.UUID] = None
    ship_id: Optional[List[uuid.UUID]] = None
    sailing_id: Optional[List[uuid.UUID]] = None
    departure_from: Optional[date] = None
    departure_to: Optional[date] = None
    archived: bool = Field(default=False, description='Include archived records')
    fx_mode: FXMode = FXMode.MANUAL
    display_currency: Optional[Currency] = None
