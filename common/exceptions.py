from common.schemas import ErrorModel
from ninja.errors import ValidationError

class APIBaseException(Exception):
    """
    Base class for all custom API exceptions.
    Ensures consistency of the error model across the application.
    Supports extra parameters for flexibility.
    """
    type = "BASE_ERROR"
    title = "An error occurred"
    status = 500

    def __init__(self, title=None, status=None, detail=None, instance=None, errors=None, **context):
        self.title = title or self.title
        self.status = status or self.status
        self.detail = detail or self.title
        self.instance = instance
        self.errors = errors
        self.context = context
        super().__init__(self.detail)

    def to_dict(self):
        return {
            "type": self.type,
            "title": self.title,
            "status": self.status,
            "detail": self.detail,
            "instance": self.instance,
            "errors": self.errors,
        }

class SeasonOverlapException(APIBaseException):
    type = "SEASON_OVERLAP"

class SailingOverlapException(APIBaseException):
    type = "SAILING_OVERLAP"

class CabinAlreadyBookedException(APIBaseException):
    type = "CABIN_ALREADY_BOOKED"

class ActiveHoldExistsException(APIBaseException):
    type = "HOLD_EXISTS"

class FXRatesStaleException(APIBaseException):
    type = "FX_STALE"

class PermissionDeniedException(APIBaseException):
    type = "PERMISSION_DENIED"

# Unnecessary since we are overriding pydantic's ValidationError exception handler
# class ValidationFailedException(APIBaseException):
#     type = "VALIDATION_FAILED"

class RateLimitedException(APIBaseException):
    type = "RATE_LIMITED"

class IdempotentReplayException(APIBaseException):
    type = "IDEMPOTENT_REPLAY"

class APIExceptionManager:
    def __init__(self, api):
        self.api = api
        self.register_handlers()

    def register_handlers(self):
        self.api.add_exception_handler(APIBaseException, self.handle_api_exception)
        self.api.add_exception_handler(ValidationError, self.handle_validation_errors)

    def handle_api_exception(self, request, exc: APIBaseException):
        error_model = ErrorModel(**exc.to_dict())
        return self.api.create_response(request, error_model, status=exc.status)

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

