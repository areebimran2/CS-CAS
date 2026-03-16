from typing import Any

from ninja import Schema


class ZohoDetailsOut(Schema):
    deal: Any
    channel: Any
    agency: Any
    agent: Any
    contact: Any

