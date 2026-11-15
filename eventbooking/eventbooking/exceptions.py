from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status


class EventNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Event not found."
    default_code = "event_not_found"


class BookingNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Booking not found."
    default_code = "booking_not_found"


class CouponNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Coupon not found."
    default_code = "coupon_not_found"


class EventCapacityError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Not enough tickets available."
    default_code = "insufficient_capacity"


class EventExpiredError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This event has already occurred."
    default_code = "event_expired"


class DuplicateBookingError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "You already have an active booking for this event."
    default_code = "duplicate_booking"


class BookingOwnershipError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permission to modify this booking."
    default_code = "booking_ownership_error"


class BookingCancellationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This booking cannot be cancelled."
    default_code = "cancellation_error"


class CancellationDeadlineError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cancellation deadline has passed. Bookings cannot be cancelled within 24 hours of the event."
    default_code = "cancellation_deadline_passed"


class CouponExpiredError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This coupon has expired."
    default_code = "coupon_expired"


class CouponUsageLimitError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This coupon has reached its maximum usage limit."
    default_code = "coupon_usage_limit"


class CouponMinimumAmountError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Order amount does not meet the minimum requirement for this coupon."
    default_code = "coupon_minimum_amount"


class CouponAlreadyUsedError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "You have already used this coupon."
    default_code = "coupon_already_used"


class InvalidQuantityError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Quantity must be between 1 and 10."
    default_code = "invalid_quantity"


def custom_exception_handler(exc, context):
    """Custom exception handler that formats all API exceptions consistently."""
    response = exception_handler(exc, context)

    if response is not None:
        error_code = getattr(exc, "default_code", "error")
        if hasattr(exc, "default_code"):
            error_code = exc.default_code

        response.data = {
            "success": False,
            "error": {
                "code": error_code,
                "message": str(exc.detail) if hasattr(exc, "detail") else str(exc),
            },
        }

    return response

