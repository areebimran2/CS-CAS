from typing import List, Optional

from ninja import Schema
from pydantic import Field

from common.enums import ImportErrorPolicy, ImportModule


# -- Requests

class ImportOptions(Schema):
    """Sent as form fields next to the CSV file."""
    error_policy: ImportErrorPolicy = ImportErrorPolicy.BLOCK_ALL
    auto_create: bool = Field(
        default=False,
        description='Create the cabin categories, amenities and custom costs the file names that don\'t exist yet. '
                    'Needs `catalogs.create`',
    )


# -- Responses

class ImportRowErrorOut(Schema):
    row: int = Field(description='1 is the first row after the header')
    column: Optional[str]
    message: str
    suggestion: Optional[str] = Field(description='e.g. the closest existing category name')


class ImportResultOut(Schema):
    """What a dry run would import, or what a commit imported."""
    module: ImportModule
    committed: bool
    rows_total: int
    rows_valid: int
    rows_invalid: int
    errors: List[ImportRowErrorOut]
    created: List[str] = Field(description='The catalogue records created by `auto_create`, e.g. "Amenity: Spa"')
