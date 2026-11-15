from django.utils import timezone
from django.db import transaction

from bookings.models import Booking
from events.models import Event, TicketType
from coupons.services.coupon_service import validate_and_apply_coupon
from bookings.utils.pricing import (
    calculate_total_price,
    calculate_discount,
    calculate_final_amount,
    calculate_refund_amount,
)
from eventbooking.exceptions import (
    EventNotFoundError,
    BookingNotFoundError,
    EventCapacityError,
    EventExpiredError,
    DuplicateBookingError,
    BookingOwnershipError,
    BookingCancellationError,
    CancellationDeadlineError,
    InvalidQuantityError,
)


def create_booking(user, event_id, ticket_type_id, quantity, coupon_code=None):
    """
    Create a new booking for a user.

    This function should:
    1. Validate the event exists and is not deleted.
    2. Validate the event has not already occurred.
    3. Validate the ticket type exists and belongs to the event.
    4. Validate quantity is between 1 and MAX_TICKETS_PER_BOOKING.
    5. Check available capacity.
    6. Check for duplicate active bookings.
    7. Apply coupon if provided.
    8. Create the booking and update capacity.

    Args:
        user: The authenticated user making the booking.
        event_id: The ID of the event to book.
        ticket_type_id: The ID of the ticket type.
        quantity: Number of tickets to book.
        coupon_code: Optional coupon code for discount.

    Returns:
        Booking instance.
    """
    # Step 1: Fetch the event
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        raise EventNotFoundError()

    # Step 2: Fetch the ticket type
    try:
        ticket_type = TicketType.objects.get(pk=ticket_type_id, event=event)
    except TicketType.DoesNotExist:
        raise EventNotFoundError("Ticket type not found for this event.")

    # Step 3: Calculate pricing
    total_amount = calculate_total_price(ticket_type.price, quantity)

    # Step 4: Apply coupon if provided
    discount_amount = 0
    coupon = None
    if coupon_code:
        coupon, discount_amount = validate_and_apply_coupon(
            coupon_code=coupon_code,
            user=user,
            order_amount=total_amount,
        )

    final_amount = calculate_final_amount(total_amount, discount_amount)

    # Step 5: Create the booking
    with transaction.atomic():
        booking = Booking.objects.create(
            user=user,
            event=event,
            ticket_type=ticket_type,
            quantity=quantity,
            total_amount=total_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            coupon=coupon,
            status="CONFIRMED",
        )

        # Update event capacity
        event.available_capacity -= quantity
        event.save()

        # Update ticket type availability
        ticket_type.quantity_available -= quantity
        ticket_type.save()

    return booking


def cancel_booking(user, booking_id, reason=""):
    """
    Cancel an existing booking.

    This function should:
    1. Validate the booking exists.
    2. Check booking ownership.
    3. Check if the booking is already cancelled.
    4. Check cancellation deadline (24 hours before event).
    5. Process the cancellation and restore capacity.

    Args:
        user: The authenticated user requesting cancellation.
        booking_id: The ID of the booking to cancel.
        reason: Optional cancellation reason.

    Returns:
        Updated Booking instance.
    """
    # Step 1: Fetch the booking
    try:
        booking = Booking.objects.select_related("event", "ticket_type").get(pk=booking_id)
    except Booking.DoesNotExist:
        raise BookingNotFoundError()

    # Step 2: Cancel the booking
    with transaction.atomic():
        booking.status = "CANCELLED"
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = reason
        booking.save()

        # Restore event capacity
        booking.event.available_capacity += booking.quantity
        booking.event.save()

        # Restore ticket type availability
        booking.ticket_type.quantity_available += booking.quantity
        booking.ticket_type.save()

    return booking


def get_user_bookings(user):
    """
    Get all bookings for a specific user.

    Args:
        user: The authenticated user.

    Returns:
        QuerySet of bookings.
    """
    return Booking.objects.filter(user=user).select_related(
        "event", "ticket_type"
    )


def get_booking_detail(user, booking_id):
    """
    Get details of a specific booking.

    Args:
        user: The authenticated user.
        booking_id: The ID of the booking.

    Returns:
        Booking instance.

    Raises:
        BookingNotFoundError: If the booking doesn't exist.
    """
    try:
        booking = Booking.objects.select_related(
            "event", "ticket_type", "coupon"
        ).get(pk=booking_id)
    except Booking.DoesNotExist:
        raise BookingNotFoundError()

    return booking

