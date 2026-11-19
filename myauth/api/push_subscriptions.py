import uuid

from ninja import Router

from common.access import requires
from myauth.schemas import PushSubscriptionIn, PushSubscriptionOut, VapidKeyOut

router = Router(tags=['N1. Browser Push'])


@router.get('/vapid-key', response=VapidKeyOut)
@requires('push.subscribe')
def get_vapid_key(request):
    """
    Returns the public VAPID key the browser needs to subscribe to push notifications.
    """


@router.get('', response=list[PushSubscriptionOut])
@requires('push.subscribe')
def list_push_subscriptions(request):
    """
    Returns the signed-in user's browser push subscriptions, one per browser they opted in on.
    """


@router.post('', response=PushSubscriptionOut)
@requires('push.subscribe')
def create_push_subscription(request, payload: PushSubscriptionIn):
    """
    Stores a browser's push subscription for the signed-in user. Which events are pushed follows their notification
    preferences in `/api/me`.
    """


@router.delete('/{subscription_id}', response={204: None})
@requires('push.subscribe')
def delete_push_subscription(request, subscription_id: uuid.UUID):
    """
    Removes one of the signed-in user's push subscriptions, e.g. when they turn notifications off in that browser.
    """
