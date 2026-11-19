import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from ninja import Schema
from pydantic import Field
from pydantic_extra_types.currency_code import Currency

from common.enums import FileFormat, FXMode, Report, SalesChannel


# -- Requests

class ReportFilter(Schema):
    """The records a report covers. Filters that don't apply to the report are ignored."""
    season_id: Optional[uuid.UUID] = None
    ship_id: Optional[List[uuid.UUID]] = None
    sailing_id: Optional[List[uuid.UUID]] = None
    route_id: Optional[uuid.UUID] = None
    category_id: Optional[List[uuid.UUID]] = None
    user_id: Optional[uuid.UUID] = Field(default=None, description='The seller, for holds and bookings')
    channel: Optional[SalesChannel] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    fx_mode: FXMode = FXMode.MANUAL
    display_currency: Optional[Currency] = None


class ReportExportIn(Schema):
    report: Report
    format: FileFormat = FileFormat.CSV
    filters: ReportFilter = ReportFilter()


# -- Responses

class ReportColumnOut(Schema):
    key: str
    label: str


class ReportOut(Schema):
    """A report as a table: one row per ship, season, sailing, user or day, depending on the report."""
    report: Report
    generated_at: datetime
    columns: List[ReportColumnOut]
    rows: List[Dict[str, Any]]
    totals: Dict[str, Any]
