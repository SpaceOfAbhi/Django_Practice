import pytest
from decimal import Decimal
from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APIClient

from bookings.models import Booking
from bookings.services.booking_service import create_booking, cancel_booking, get_booking_detail
from eventbooking.exceptions import (
    EventNotFoundError,
    EventCapacityError,
    EventExpiredError,
    DuplicateBookingError,
    BookingNotFoundError,
    BookingOwnershipError,
    BookingCancellationError,
    CancellationDeadlineError,
    InvalidQuantityError,
)


# ===========================================================================
# BOOKING CREATION TESTS
# ===========================================================================

class TestCreateBookingSuccess:
    """Tests for successful booking creation."""

    def test_create_basic_booking(self, user, future_event, general_ticket):
        """Should successfully create a booking with valid inputs."""
        booking = create_booking(
            user=user,
            event_id=future_event.id,
            ticket_type_id=general_ticket.id,
            quantity=2,
        )
        assert booking is not None
        assert booking.status == "CONFIRMED"
        assert booking.quantity == 2
        assert booking.total_amount == Decimal("100.00")
        assert booking.final_amount == Decimal("100.00")
        assert booking.user == user

    def test_create_booking_updates_capacity(self, user, future_event, general_ticket):
        """Booking creation should reduce available capacity."""
        initial_capacity = future_event.available_capacity
        create_booking(
            user=user,
            event_id=future_event.id,
            ticket_type_id=general_ticket.id,
            quantity=3,
        )
        future_event.refresh_from_db()
        assert future_event.available_capacity == initial_capacity - 3

    def test_create_booking_with_valid_coupon(
        self, user, future_event, general_ticket, valid_coupon
    ):
        """Should apply coupon discount when a valid coupon is provided."""
        booking = create_booking(
            user=user,
            event_id=future_event.id,
            ticket_type_id=general_ticket.id,
            quantity=2,
            coupon_code="SAVE20",
        )
        assert booking.coupon == valid_coupon
        assert booking.discount_amount > 0
        assert booking.final_amount < booking.total_amount

    def test_create_booking_single_ticket(self, user, future_event, general_ticket):
        """Should allow booking a single ticket."""
        booking = create_booking(
            user=user,
            event_id=future_event.id,
            ticket_type_id=general_ticket.id,
            quantity=1,
        )
        assert booking.quantity == 1
        assert booking.total_amount == Decimal("50.00")


# ===========================================================================
# BOOKING CREATION FAILURE TESTS
# ===========================================================================

class TestCreateBookingFailures:
    """Tests for booking creation failures and validation."""

    def test_booking_nonexistent_event(self, user, general_ticket):
        """Should raise EventNotFoundError for non-existent event."""
        with pytest.raises(EventNotFoundError):
            create_booking(
                user=user,
                event_id=99999,
                ticket_type_id=general_ticket.id,
                quantity=1,
            )

    def test_booking_deleted_event(self, user, deleted_event, deleted_event_ticket):
        """
        Should raise EventNotFoundError for a soft-deleted event.
        Deleted events must not accept bookings.
        """
        with pytest.raises(EventNotFoundError):
            create_booking(
                user=user,
                event_id=deleted_event.id,
                ticket_type_id=deleted_event_ticket.id,
                quantity=1,
            )

    def test_booking_past_event(self, user, past_event, past_event_ticket):
        """
        Should raise EventExpiredError for an event that has already occurred.
        """
        with pytest.raises(EventExpiredError):
            create_booking(
                user=user,
                event_id=past_event.id,
                ticket_type_id=past_event_ticket.id,
                quantity=1,
            )

    def test_booking_sold_out_event(self, user, sold_out_event, sold_out_ticket):
        """
        Should raise EventCapacityError when event has no available capacity.
        """
        with pytest.raises(EventCapacityError):
            create_booking(
                user=user,
                event_id=sold_out_event.id,
                ticket_type_id=sold_out_ticket.id,
                quantity=1,
            )

    def test_booking_exceeds_capacity(self, user, low_capacity_event, low_capacity_ticket):
        """
        Should raise EventCapacityError when requested quantity exceeds
        available capacity.
        """
        with pytest.raises(EventCapacityError):
            create_booking(
                user=user,
                event_id=low_capacity_event.id,
                ticket_type_id=low_capacity_ticket.id,
                quantity=5,  # Only 3 available
            )

    def test_duplicate_booking_same_event(self, user, future_event, general_ticket):
        """
        Should raise DuplicateBookingError when user already has an active
        booking for the same event.
        """
        # First booking succeeds
        create_booking(
            user=user,
            event_id=future_event.id,
            ticket_type_id=general_ticket.id,
            quantity=1,
        )

        # Second booking for same event should fail
        with pytest.raises(DuplicateBookingError):
            create_booking(
                user=user,
                event_id=future_event.id,
                ticket_type_id=general_ticket.id,
                quantity=1,
            )

    def test_invalid_quantity_zero(self, user, future_event, general_ticket):
        """Should raise InvalidQuantityError for quantity of 0."""
        with pytest.raises(InvalidQuantityError):
            create_booking(
                user=user,
                event_id=future_event.id,
                ticket_type_id=general_ticket.id,
                quantity=0,
            )

    def test_invalid_quantity_negative(self, user, future_event, general_ticket):
        """Should raise InvalidQuantityError for negative quantity."""
        with pytest.raises(InvalidQuantityError):
            create_booking(
                user=user,
                event_id=future_event.id,
                ticket_type_id=general_ticket.id,
                quantity=-1,
            )

    def test_invalid_quantity_exceeds_max(self, user, future_event, general_ticket):
        """Should raise InvalidQuantityError for quantity exceeding maximum (10)."""
        with pytest.raises(InvalidQuantityError):
            create_booking(
                user=user,
                event_id=future_event.id,
                ticket_type_id=general_ticket.id,
                quantity=11,
            )

    def test_booking_does_not_update_capacity_on_failure(
        self, user, sold_out_event, sold_out_ticket
    ):
        """Available capacity should not change when booking fails."""
        initial_capacity = sold_out_event.available_capacity
        with pytest.raises(EventCapacityError):
            create_booking(
                user=user,
                event_id=sold_out_event.id,
                ticket_type_id=sold_out_ticket.id,
                quantity=1,
            )
        sold_out_event.refresh_from_db()
        assert sold_out_event.available_capacity == initial_capacity


# ===========================================================================
# BOOKING CANCELLATION TESTS
# ===========================================================================

class TestCancelBookingSuccess:
    """Tests for successful booking cancellation."""

    def test_cancel_own_booking(self, user, future_event, general_ticket):
        """User should be able to cancel their own booking."""
        booking = create_booking(
            user=user,
            event_id=future_event.id,
            ticket_type_id=general_ticket.id,
            quantity=2,
        )
        cancelled = cancel_booking(user=user, booking_id=booking.id, reason="Changed plans")
        assert cancelled.status == "CANCELLED"
        assert cancelled.cancelled_at is not None
        assert cancelled.cancellation_reason == "Changed plans"

    def test_cancel_booking_restores_capacity(self, user, future_event, general_ticket):
        """Cancelling a booking should restore event capacity."""
        booking = create_booking(
            user=user,
            event_id=future_event.id,
            ticket_type_id=general_ticket.id,
            quantity=2,
        )
        capacity_after_booking = future_event.available_capacity
        future_event.refresh_from_db()
        capacity_after_booking = future_event.available_capacity

        cancel_booking(user=user, booking_id=booking.id)
        future_event.refresh_from_db()
        assert future_event.available_capacity == capacity_after_booking + 2


class TestCancelBookingFailures:
    """Tests for booking cancellation failures."""

    def test_cancel_nonexistent_booking(self, user):
        """Should raise BookingNotFoundError for non-existent booking."""
        with pytest.raises(BookingNotFoundError):
            cancel_booking(user=user, booking_id=99999)

    def test_cancel_other_users_booking(
        self, user, other_user, future_event, general_ticket
    ):
        """
        Should raise BookingOwnershipError when trying to cancel
        another user's booking.
        """
        booking = create_booking(
            user=user,
            event_id=future_event.id,
            ticket_type_id=general_ticket.id,
            quantity=1,
        )

        with pytest.raises(BookingOwnershipError):
            cancel_booking(user=other_user, booking_id=booking.id)

    def test_cancel_already_cancelled_booking(
        self, user, future_event, general_ticket
    ):
        """
        Should raise BookingCancellationError when trying to cancel
        an already cancelled booking.
        """
        booking = create_booking(
            user=user,
            event_id=future_event.id,
            ticket_type_id=general_ticket.id,
            quantity=1,
        )
        cancel_booking(user=user, booking_id=booking.id)

        with pytest.raises(BookingCancellationError):
            cancel_booking(user=user, booking_id=booking.id)

    def test_cancel_within_deadline(
        self, user, event_happening_soon, soon_event_ticket
    ):
        """
        Should raise CancellationDeadlineError when trying to cancel
        within 24 hours of the event.
        """
        booking = create_booking(
            user=user,
            event_id=event_happening_soon.id,
            ticket_type_id=soon_event_ticket.id,
            quantity=1,
        )

        with pytest.raises(CancellationDeadlineError):
            cancel_booking(user=user, booking_id=booking.id)

    def test_cancel_does_not_restore_capacity_on_failure(
        self, user, other_user, future_event, general_ticket
    ):
        """Capacity should not change when cancellation fails."""
        booking = create_booking(
            user=user,
            event_id=future_event.id,
            ticket_type_id=general_ticket.id,
            quantity=2,
        )
        future_event.refresh_from_db()
        capacity_after_booking = future_event.available_capacity

        with pytest.raises(BookingOwnershipError):
            cancel_booking(user=other_user, booking_id=booking.id)

        future_event.refresh_from_db()
        assert future_event.available_capacity == capacity_after_booking


# ===========================================================================
# BOOKING DETAIL TESTS
# ===========================================================================

class TestBookingDetail:
    """Tests for retrieving booking details."""

    def test_get_own_booking_detail(self, user, future_event, general_ticket):
        """User should be able to view their own booking details."""
        booking = create_booking(
            user=user,
            event_id=future_event.id,
            ticket_type_id=general_ticket.id,
            quantity=1,
        )
        result = get_booking_detail(user=user, booking_id=booking.id)
        assert result.id == booking.id

    def test_get_nonexistent_booking(self, user):
        """Should raise BookingNotFoundError for non-existent booking."""
        with pytest.raises(BookingNotFoundError):
            get_booking_detail(user=user, booking_id=99999)

    def test_get_other_users_booking_should_fail(
        self, user, other_user, future_event, general_ticket
    ):
        """
        Should raise BookingOwnershipError when trying to view
        another user's booking details.
        """
        booking = create_booking(
            user=user,
            event_id=future_event.id,
            ticket_type_id=general_ticket.id,
            quantity=1,
        )

        with pytest.raises(BookingOwnershipError):
            get_booking_detail(user=other_user, booking_id=booking.id)


# ===========================================================================
# API ENDPOINT TESTS
# ===========================================================================

class TestBookingAPI:
    """Tests for booking API endpoints."""

    def test_create_booking_api_success(self, user, future_event, general_ticket):
        """POST /api/bookings/create/ should create a booking."""
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            "/api/bookings/create/",
            {
                "event_id": future_event.id,
                "ticket_type_id": general_ticket.id,
                "quantity": 2,
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.data["success"] is True
        assert response.data["data"]["quantity"] == 2

    def test_create_booking_api_deleted_event(
        self, user, deleted_event, deleted_event_ticket
    ):
        """POST /api/bookings/create/ with deleted event should return 404."""
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            "/api/bookings/create/",
            {
                "event_id": deleted_event.id,
                "ticket_type_id": deleted_event_ticket.id,
                "quantity": 1,
            },
            format="json",
        )
        assert response.status_code == 404

    def test_create_booking_api_past_event(
        self, user, past_event, past_event_ticket
    ):
        """POST /api/bookings/create/ with past event should return 400."""
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            "/api/bookings/create/",
            {
                "event_id": past_event.id,
                "ticket_type_id": past_event_ticket.id,
                "quantity": 1,
            },
            format="json",
        )
        assert response.status_code == 400

    def test_cancel_booking_api_success(self, user, future_event, general_ticket):
        """POST /api/bookings/<id>/cancel/ should cancel the booking."""
        client = APIClient()
        client.force_authenticate(user=user)

        # First create a booking
        booking = create_booking(
            user=user,
            event_id=future_event.id,
            ticket_type_id=general_ticket.id,
            quantity=1,
        )

        response = client.post(
            f"/api/bookings/{booking.id}/cancel/",
            {"reason": "Cannot attend"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["data"]["status"] == "CANCELLED"

    def test_cancel_booking_api_forbidden(
        self, user, other_user, future_event, general_ticket
    ):
        """POST /api/bookings/<id>/cancel/ by another user should return 403."""
        client = APIClient()

        booking = create_booking(
            user=user,
            event_id=future_event.id,
            ticket_type_id=general_ticket.id,
            quantity=1,
        )

        client.force_authenticate(user=other_user)
        response = client.post(
            f"/api/bookings/{booking.id}/cancel/",
            {"reason": "Hacking attempt"},
            format="json",
        )
        assert response.status_code == 403

    def test_unauthenticated_booking_attempt(self, future_event, general_ticket):
        """POST /api/bookings/create/ without auth should return 403."""
        client = APIClient()
        response = client.post(
            "/api/bookings/create/",
            {
                "event_id": future_event.id,
                "ticket_type_id": general_ticket.id,
                "quantity": 1,
            },
            format="json",
        )
        assert response.status_code == 403

