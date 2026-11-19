from ninja import Router

from common.access import requires
from common.enums import ImportModule

router = Router(tags=['K1. Import'])


@router.get('/{module}')
@requires('data.import')
def get_import_template(request, module: ImportModule):
    """
    Downloads the CSV template for a module: the header row and one sample row.
    """
