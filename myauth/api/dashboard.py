from ninja import Router

from common.access import authenticated
from myauth.schemas import DashboardLayout

router = Router(tags=['M2. Dashboard Layout'])


@router.get('', response=DashboardLayout)
@authenticated
def get_dashboard_layout(request):
    """
    Returns the signed-in user's dashboard: which widgets are shown and where, their FX mode and default date range.
    The widgets' data comes from the endpoints they summarise (sailings, reports, discounts).
    """


@router.put('', response=DashboardLayout)
@authenticated
def replace_dashboard_layout(request, payload: DashboardLayout):
    """
    Replaces the signed-in user's dashboard layout.
    """
