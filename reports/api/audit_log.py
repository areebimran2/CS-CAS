from ninja import Query, Router
from ninja_extra import paginate
from ninja_extra.schemas import NinjaPaginationResponseSchema

from common.access import requires
from reports.schemas import AuditLogFilter, AuditLogOut

router = Router(tags=['Q1. Audit Log'])


@router.get('', response=NinjaPaginationResponseSchema[AuditLogOut])
@requires('audit.view')
@paginate()
def list_audit_log(request, filters: Query[AuditLogFilter]):
    """
    Returns audit entries, newest first, with the record's state before and after each change. Filter by record
    (`entity` and `entity_id`), by who made the change, by action or by time.
    """
