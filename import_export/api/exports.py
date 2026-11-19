from ninja import Query, Router

from common.access import requires
from common.enums import ExportModule
from import_export.schemas import ExportOptions

router = Router(tags=['K2. Export'])


@router.get('/{module}')
@requires('data.export')
def export_module(request, module: ExportModule, options: Query[ExportOptions]):
    """
    Downloads a module's records as CSV or PDF, matching the filters, with totals where relevant.
    """
