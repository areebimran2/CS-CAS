from ninja import Query, Router

from common.access import requires
from common.enums import Report
from reports.schemas import ReportExportIn, ReportFilter, ReportOut

router = Router(tags=['L1. Reports'])

# Django tries paths in the order they're declared, so /export must come before /{report}.


@router.post('/export')
@requires('reports.view')
def export_report(request, payload: ReportExportIn):
    """
    Downloads a report as CSV or PDF, with the same filters as viewing it.
    """


@router.get('/{report}', response=ReportOut)
@requires('reports.view')
def get_report(request, report: Report, filters: Query[ReportFilter]):
    """
    Runs a report: utilisation, pricing coverage, holds and conversions, bookings, cancellations, discount uplift,
    cost-of-sale roll-up or pickup curve. Amounts are shown in the chosen FX mode.
    """
