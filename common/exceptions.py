from common.schemas import ErrorModel
from ninja.errors import ValidationError, HttpError


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
        super().__init__(status_code=status, message=title)

    def to_dict(self):
        return {
            "type": self.type,
            "title": self.title,
            "status": self.status,
            "detail": self.detail,
            "instance": self.instance,
            "errors": self.errors,
        }

class SeasonOverlapError(APIBaseError):
    type = "SEASON_OVERLAP"

class SailingOverlapError(APIBaseError):
    type = "SAILING_OVERLAP"

class CabinAlreadyBookedError(APIBaseError):
    type = "CABIN_ALREADY_BOOKED"

class ActiveHoldExistsError(APIBaseError):
    type = "HOLD_EXISTS"

class FXRatesStaleError(APIBaseError):
    type = "FX_STALE"

class PermissionDeniedError(APIBaseError):
    type = "PERMISSION_DENIED"

# Specific Error for validation failures
class ValidationFailedError(APIBaseError):
    type = "VALIDATION_FAILED"

class RateLimitedError(APIBaseError):
    type = "RATE_LIMITED"

class IdempotentReplayError(APIBaseError):
    type = "IDEMPOTENT_REPLAY"

class APIErrorManager:
    def __init__(self, api):
        self.api = api
        self.register_handlers()

    def register_handlers(self):
        self.api.add_exception_handler(APIBaseError, self.handle_api_errors)
        self.api.add_exception_handler(ValidationError, self.handle_validation_errors)

    def handle_api_errors(self, request, exc: APIBaseError):
        error_model = ErrorModel(**exc.to_dict())
        error_model.instance = request.path
        return self.api.create_response(request, error_model, status=exc.status)

    # Override for ValidationError to provide detailed error information
    def handle_validation_errors(self, request, exc: ValidationError):
        error_model = ErrorModel(
            type="VALIDATION_FAILED",
            title="Validation Failed",
            status=400,
            detail="One or more validation errors occurred.",
            instance=request.path,
            errors=exc.errors
        )

        return self.api.create_response(request, error_model, status=422)

