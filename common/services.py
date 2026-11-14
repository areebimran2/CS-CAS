"""Helpers shared by the services in every app."""


def update_instance(instance, changes: dict):
    """Set each field in `changes` on a model instance, save it, and return it. Used by update services."""
    for field, value in changes.items():
        setattr(instance, field, value)
    instance.save()
    return instance
