from typing import Annotated, Any, Dict, List, Literal, Optional

from django.db.models import Q
from ninja import FilterSchema, Schema
from pydantic import BeforeValidator, StringConstraints


class ErrorModel(Schema):
    type: str
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = None


# -- Reusable field types for request schemas

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
"""Text with surrounding spaces removed, which must not be empty."""


def _blank_to_none(value):
    return (value.strip() or None) if isinstance(value, str) else value


OptionalStr = Annotated[Optional[str], BeforeValidator(_blank_to_none)]
"""Optional text with surrounding spaces removed. Blank text becomes null."""


# -- List filters

class ArchivedFilter(FilterSchema):
    """
    Base for the list filters of records that can be archived. `?archived=false` (the default) lists current records,
    `true` lists archived ones, and `all` lists both.
    """
    archived: Literal['false', 'true', 'all'] = 'false'

    def filter_archived(self, value):
        return {'false': Q(is_archived=False), 'true': Q(is_archived=True), 'all': Q()}[value]
