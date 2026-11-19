"""Helpers shared by the services in every app."""
from django.db import router
from django.db.models.deletion import Collector, ProtectedError, RestrictedError

from common.exceptions import InUseError


def update_instance(instance, changes: dict):
    """Set each field in `changes` on a model instance, save it, and return it. Used by update services."""
    for field, value in changes.items():
        setattr(instance, field, value)
    instance.save()
    return instance


def delete_if_unused(instance, *, owned=()) -> None:
    """
    Delete `instance` and the rows it owns, unless any other record refers to it (spec: "used records are archived,
    not deleted").

    `owned` lists the models whose rows belong to the instance and go with it, such as a ship's currencies. Every other
    reference blocks the delete with 409 IN_USE, whatever its on_delete setting. Django's deletion collector finds the
    references, so ones added by later modules are covered without changing this code.
    """
    collector = Collector(using=router.db_for_write(type(instance)))
    try:
        collector.collect([instance])
    except ProtectedError as exc:
        blocking = {type(obj) for obj in exc.protected_objects}
    except RestrictedError as exc:
        blocking = {type(obj) for obj in exc.restricted_objects}
    else:
        affected = {model for model, rows in collector.data.items() if rows}
        affected |= {queryset.model for queryset in collector.fast_deletes if queryset.exists()}
        blocking = affected - {type(instance), *owned}

    if blocking:
        names = ', '.join(sorted(str(model._meta.verbose_name_plural) for model in blocking))
        raise InUseError(detail=f'This {instance._meta.verbose_name} is still referred to by: {names}. '
                                'Archive it instead.')
    collector.delete()
