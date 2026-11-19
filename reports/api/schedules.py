import uuid

from ninja import Router

from common.access import requires
from reports.schemas import ReportScheduleIn, ReportScheduleOut

router = Router(tags=['L2. Report Schedules'])


@router.get('', response=list[ReportScheduleOut])
@requires('reports.schedule')
def list_report_schedules(request):
    """
    Returns the report schedules by name.
    """


@router.post('', response=ReportScheduleOut)
@requires('reports.schedule')
def create_report_schedule(request, payload: ReportScheduleIn):
    """
    Schedules a report to be emailed to its recipients daily, weekly or monthly at the given time.
    """


@router.get('/{schedule_id}', response=ReportScheduleOut)
@requires('reports.schedule')
def get_report_schedule(request, schedule_id: uuid.UUID):
    """
    Returns a report schedule.
    """


@router.put('/{schedule_id}', response=ReportScheduleOut)
@requires('reports.schedule')
def replace_report_schedule(request, payload: ReportScheduleIn, schedule_id: uuid.UUID):
    """
    Replaces a report schedule. Set `is_active` to false to pause it.
    """


@router.delete('/{schedule_id}', response={204: None})
@requires('reports.schedule')
def delete_report_schedule(request, schedule_id: uuid.UUID):
    """
    Deletes a report schedule.
    """
