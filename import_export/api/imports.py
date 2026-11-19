from typing import Optional

from ninja import File, Form, Header, Router, UploadedFile

from common.access import requires
from common.enums import ImportModule
from import_export.schemas import ImportOptions, ImportResultOut

router = Router(tags=['K1. Import'])


@router.post('/{module}/dry-run', response=ImportResultOut)
@requires('data.import')
def dry_run_import(request, module: ImportModule, file: File[UploadedFile], options: Form[ImportOptions]):
    """
    Validates a CSV file without saving anything, and returns each invalid row with a suggested fix. Season imports
    are blocked when a season overlaps another.
    """


@router.post('/{module}/commit', response=ImportResultOut)
@requires('data.import')
def commit_import(request, module: ImportModule, file: File[UploadedFile], options: Form[ImportOptions],
                  idempotency_key: Optional[str] = Header(default=None, alias='Idempotency-Key')):
    """
    Imports a CSV file in one transaction. With `error_policy=block_all` nothing is imported when any row is invalid;
    with `skip_invalid` the valid rows are. Repeating a request with the same `Idempotency-Key` returns the first
    result.
    """
