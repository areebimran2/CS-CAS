from typing import List, Optional

from ninja import Schema

from common.enums import SalesChannel
from common.schemas import NonEmptyStr


class UcRefIn(Schema):
    uc_ref: NonEmptyStr


class ZohoContactOut(Schema):
    name: str
    email: Optional[str]
    phone: Optional[str]


class ZohoDetailsOut(Schema):
    """The Zoho deal behind a UC Ref, used to prefill holds and bookings (spec J)."""
    uc_ref: str
    deal_name: str
    channel: SalesChannel
    agency: Optional[str]
    agent: Optional[str]
    contacts: List[ZohoContactOut]
