import psycopg
from django.apps import apps
from django.db import IntegrityError
from django.db.models import UniqueConstraint
from ninja.errors import AuthenticationError, HttpError, ValidationError

from common.schemas import ErrorModel


class APIBaseError(HttpError):
    """
    Base class for all custom API errors.
    Ensures consistency of the error model across the application.
    Supports extra parameters for flexibility.
    """
    type = "BASE_ERROR"
    title = "An error occurred"
    status = 500

    def __init__(self, title=None, status=None, detail=None, instance=None, errors=None):
        self.title = title or self.title
        self.status = status or self.status
        self.detail = detail or self.title
        self.instance = instance
        self.errors = errors
        super().__init__(status_code=self.status, message=self.title)

    def to_dict(self):
        return {
            "type": self.type,
            "title": self.title,
            "status": self.status,
            "detail": self.detail,
            "instance": self.instance,
            "errors": self.errors or [],
        }

class SeasonOverlapError(APIBaseError):
    type = "SEASON_OVERLAP"
    title = "Seasons may not overlap"
    status = 409

class SailingOverlapError(APIBaseError):
    type = "SAILING_OVERLAP"
    title = "This ship already has a sailing on these dates"
    status = 409

class CabinAlreadyBookedError(APIBaseError):
    type = "CABIN_ALREADY_BOOKED"
    title = "Cabin already booked"
    status = 409

class ActiveHoldExistsError(APIBaseError):
    type = "HOLD_EXISTS"
    title = "Cabin is held by someone else"
    status = 409

class FXRatesStaleError(APIBaseError):
    type = "FX_STALE"
    title = "Live exchange rates are out of date"
    status = 409

class NotAuthenticatedError(APIBaseError):
    type = "NOT_AUTHENTICATED"
    title = "Authentication required"
    status = 401

class PermissionDeniedError(APIBaseError):
    type = "PERMISSION_DENIED"
    title = "Permission denied"
    status = 403

class ValidationFailedError(APIBaseError):
    """A request that is well-formed but breaks a business rule. `errors` names each offending field."""
    type = "VALIDATION_FAILED"
    title = "Validation failed"
    status = 422

class DuplicateError(APIBaseError):
    """Raised automatically when a save breaks a unique constraint (see APIErrorManager.handle_integrity_errors)."""
    type = "DUPLICATE"
    title = "Already exists"
    status = 409

class InUseError(APIBaseError):
    """A record that other records still refer to can't be deleted; archive it instead."""
    type = "IN_USE"
    title = "Still in use"
    status = 409

class ShipArchivedError(APIBaseError):
    type = "SHIP_ARCHIVED"
    title = "Ship is archived"
    status = 409

class RateLimitedError(APIBaseError):
    type = "RATE_LIMITED"
    title = "Too many attempts"
    status = 429

class IdempotentReplayError(APIBaseError):
    type = "IDEMPOTENT_REPLAY"
    title = "Request already processed"
    status = 409

class APIErrorManager:
    def __init__(self, api):
        self.api = api
        self.register_handlers()

    def register_handlers(self):
        self.api.add_exception_handler(APIBaseError, self.handle_api_errors)
        self.api.add_exception_handler(ValidationError, self.handle_validation_errors)
        # ninja raises this when a protected endpoint is called without an access token
        self.api.add_exception_handler(AuthenticationError, self.handle_missing_credentials)
        self.api.add_exception_handler(IntegrityError, self.handle_integrity_errors)

    def handle_api_errors(self, request, exc: APIBaseError):
        error_model = ErrorModel(**exc.to_dict())
        error_model.instance = request.path
        return self.api.create_response(request, error_model, status=exc.status)

    # Override for ValidationError to provide detailed error information
    def handle_validation_errors(self, request, exc: ValidationError):
        error_model = ErrorModel(
            type="VALIDATION_FAILED",
            title="Validation Failed",
            status=422,
            detail="One or more validation errors occurred.",
            instance=request.path,
            errors=exc.errors
        )

        return self.api.create_response(request, error_model, status=422)

    def handle_missing_credentials(self, request, exc: AuthenticationError):
        error = NotAuthenticatedError(detail='Send an access token in the header: Authorization: Bearer <token>')
        return self.handle_api_errors(request, error)

    def handle_integrity_errors(self, request, exc: IntegrityError):
        """
        A save that breaks a unique constraint becomes 409 DUPLICATE, naming the fields. The database constraint is
        the real guard, so two simultaneous requests can't both succeed, and services need no duplicate checks of
        their own. Any other integrity error is a bug, so it is raised as a 500.
        """
        violated = _violated_unique_constraint(exc)
        if violated is None:
            raise exc
        model, constraint = violated
        # Leave out the parent the record belongs to: a cabin number is unique "on this ship".
        fields = [name for name in constraint.fields if not model._meta.get_field(name).is_relation]
        fields = fields or list(constraint.fields)
        error = DuplicateError(
            detail=f"A {model._meta.verbose_name} with this {' and '.join(fields)} already exists.",
            errors=[{'field': name, 'message': 'Already in use'} for name in fields],
        )
        return self.handle_api_errors(request, error)


def _violated_unique_constraint(exc: IntegrityError):
    """The (model, UniqueConstraint) that `exc` broke, or None if it isn't a unique violation of a known constraint."""
    if not isinstance(exc.__cause__, psycopg.errors.UniqueViolation):
        return None
    name = exc.__cause__.diag.constraint_name
    for model in apps.get_models():
        for constraint in model._meta.constraints:
            if isinstance(constraint, UniqueConstraint) and constraint.name == name:
                return model, constraint
    return None

