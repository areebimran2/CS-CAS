import uuid
from datetime import datetime, time
from typing import List, Optional

from ninja import Schema
from pydantic import EmailStr, Field

from common.enums import FileFormat, Report, ReportFrequency
from common.schemas import NonEmptyStr
from reports.schemas.reports import ReportFilter


# -- Requests

class ReportScheduleIn(Schema):
    """A report emailed to recipients daily, weekly or monthly (spec M, "Scheduling")."""
    name: NonEmptyStr
    report: Report
    filters: ReportFilter = ReportFilter()
    format: FileFormat = FileFormat.PDF
    frequency: ReportFrequency
    weekday: Optional[int] = Field(default=None, ge=1, le=7, description='1 is Monday. Weekly schedules only')
    day_of_month: Optional[int] = Field(default=None, ge=1, le=28, description='Monthly schedules only')
    send_at: time
    timezone: NonEmptyStr = Field(default='UTC', description='IANA name, e.g. Europe/Malta')
    recipients: List[EmailStr] = Field(min_length=1)
    is_active: bool = True


# -- Responses

class ReportScheduleOut(ReportScheduleIn):
    id: uuid.UUID
    next_run_at: Optional[datetime] = Field(description='None when the schedule is paused')
