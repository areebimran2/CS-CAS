from typing import Any, Dict, List, Optional

from ninja import Schema


class ErrorModel(Schema):
    type: str
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = None

