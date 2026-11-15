import pytest
from decimal import Decimal
from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from events.models import Event, TicketType
from coupons.models import Coupon, CouponUsage


@pytest.fixture
def organizer(db):
    """Create an event organizer user."""
    return User.objects.create_user(
        username="organizer",
        email="organizer@example.com",
        password="testpass123",
        first_name="Event",
        last_name="Organizer",
    )


@pytest.fixture
def user(db):
    """Create a regular user."""
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def other_user(db):
    """Create another regular user."""
    return User.objects.create_user(
        username="otheruser",
        email="other@example.com",
        password="testpass123",
        first_name="Other",
        last_name="User",
    )


@pytest.fixture
def future_event(db, organizer):
    """Create a future event with available capacity."""
    return Event.objects.create(
        name="Django Conference 2027",
        description="Annual Django developer conference.",
        venue="Convention Center",
        event_date=timezone.now() + timedelta(days=30),
        total_capacity=100,
        available_capacity=100,
        organizer=organizer,
    )


@pytest.fixture
def past_event(db, organizer):
    """Create an event that has already occurred."""
    return Event.objects.create(
        name="Python Workshop 2024",
        description="Introductory Python workshop.",
        venue="Tech Hub",
        event_date=timezone.now() - timedelta(days=5),
        total_capacity=50,
        available_capacity=50,
        organizer=organizer,
    )


@pytest.fixture
def deleted_event(db, organizer):
    """Create a soft-deleted event."""
    return Event.objects.create(
        name="Cancelled Meetup",
        description="This event was cancelled.",
        venue="Community Hall",
        event_date=timezone.now() + timedelta(days=15),
        total_capacity=30,
        available_capacity=30,
        organizer=organizer,
        is_deleted=True,
    )


@pytest.fixture
def sold_out_event(db, organizer):
    """Create a sold-out event."""
    return Event.objects.create(
        name="Exclusive Gala",
        description="Limited seats gala dinner.",
        venue="Grand Hotel",
        event_date=timezone.now() + timedelta(days=20),
        total_capacity=10,
        available_capacity=0,
        organizer=organizer,
    )


@pytest.fixture
def low_capacity_event(db, organizer):
    """Create an event with very limited capacity."""
    return Event.objects.create(
        name="Workshop: Advanced Django",
        description="Small-group advanced workshop.",
        venue="Training Room A",
        event_date=timezone.now() + timedelta(days=10),
        total_capacity=20,
        available_capacity=3,
        organizer=organizer,
    )


@pytest.fixture
def event_happening_soon(db, organizer):
    """Create an event happening within 12 hours (within cancellation deadline)."""
    return Event.objects.create(
        name="Tonight's Meetup",
        description="Casual developer meetup.",
        venue="Cafe Code",
        event_date=timezone.now() + timedelta(hours=12),
        total_capacity=40,
        available_capacity=40,
        organizer=organizer,
    )


@pytest.fixture
def general_ticket(db, future_event):
    """Create a general admission ticket type."""
    return TicketType.objects.create(
        event=future_event,
        name="General Admission",
        price=Decimal("50.00"),
        quantity_available=80,
        is_active=True,
    )


@pytest.fixture
def vip_ticket(db, future_event):
    """Create a VIP ticket type."""
    return TicketType.objects.create(
        event=future_event,
        name="VIP",
        price=Decimal("150.00"),
        quantity_available=20,
        is_active=True,
    )


@pytest.fixture
def past_event_ticket(db, past_event):
    """Create a ticket type for the past event."""
    return TicketType.objects.create(
        event=past_event,
        name="Standard",
        price=Decimal("30.00"),
        quantity_available=50,
        is_active=True,
    )


@pytest.fixture
def deleted_event_ticket(db, deleted_event):
    """Create a ticket type for the deleted event."""
    return TicketType.objects.create(
        event=deleted_event,
        name="Standard",
        price=Decimal("25.00"),
        quantity_available=30,
        is_active=True,
    )


@pytest.fixture
def sold_out_ticket(db, sold_out_event):
    """Create a ticket type for the sold-out event."""
    return TicketType.objects.create(
        event=sold_out_event,
        name="Standard",
        price=Decimal("200.00"),
        quantity_available=0,
        is_active=True,
    )


@pytest.fixture
def low_capacity_ticket(db, low_capacity_event):
    """Create a ticket type for the low capacity event."""
    return TicketType.objects.create(
        event=low_capacity_event,
        name="Workshop Pass",
        price=Decimal("75.00"),
        quantity_available=3,
        is_active=True,
    )


@pytest.fixture
def soon_event_ticket(db, event_happening_soon):
    """Create a ticket type for the event happening soon."""
    return TicketType.objects.create(
        event=event_happening_soon,
        name="Entry Pass",
        price=Decimal("20.00"),
        quantity_available=40,
        is_active=True,
    )


@pytest.fixture
def valid_coupon(db):
    """Create a valid active coupon."""
    return Coupon.objects.create(
        code="SAVE20",
        discount_type="PERCENTAGE",
        discount_value=Decimal("20.00"),
        min_order_amount=Decimal("50.00"),
        max_uses=100,
        current_uses=10,
        valid_from=timezone.now() - timedelta(days=10),
        valid_until=timezone.now() + timedelta(days=30),
        is_active=True,
    )


@pytest.fixture
def expired_coupon(db):
    """Create an expired coupon."""
    return Coupon.objects.create(
        code="EXPIRED50",
        discount_type="FIXED",
        discount_value=Decimal("50.00"),
        min_order_amount=Decimal("100.00"),
        max_uses=50,
        current_uses=20,
        valid_from=timezone.now() - timedelta(days=60),
        valid_until=timezone.now() - timedelta(days=1),
        is_active=True,
    )


@pytest.fixture
def maxed_out_coupon(db):
    """Create a coupon that has reached its usage limit."""
    return Coupon.objects.create(
        code="MAXED",
        discount_type="PERCENTAGE",
        discount_value=Decimal("10.00"),
        min_order_amount=Decimal("0.00"),
        max_uses=5,
        current_uses=5,
        valid_from=timezone.now() - timedelta(days=10),
        valid_until=timezone.now() + timedelta(days=30),
        is_active=True,
    )


@pytest.fixture
def inactive_coupon(db):
    """Create an inactive coupon."""
    return Coupon.objects.create(
        code="INACTIVE",
        discount_type="FIXED",
        discount_value=Decimal("25.00"),
        min_order_amount=Decimal("0.00"),
        max_uses=0,
        current_uses=0,
        valid_from=timezone.now() - timedelta(days=10),
        valid_until=timezone.now() + timedelta(days=30),
        is_active=False,
    )


@pytest.fixture
def deleted_coupon(db):
    """Create a soft-deleted coupon."""
    return Coupon.objects.create(
        code="DELETED",
        discount_type="PERCENTAGE",
        discount_value=Decimal("15.00"),
        min_order_amount=Decimal("0.00"),
        max_uses=0,
        current_uses=0,
        valid_from=timezone.now() - timedelta(days=10),
        valid_until=timezone.now() + timedelta(days=30),
        is_active=True,
        is_deleted=True,
    )


@pytest.fixture
def high_minimum_coupon(db):
    """Create a coupon with a high minimum order amount."""
    return Coupon.objects.create(
        code="BIGORDER",
        discount_type="FIXED",
        discount_value=Decimal("100.00"),
        min_order_amount=Decimal("500.00"),
        max_uses=0,
        current_uses=0,
        valid_from=timezone.now() - timedelta(days=10),
        valid_until=timezone.now() + timedelta(days=30),
        is_active=True,
    )


@pytest.fixture
def fixed_coupon(db):
    """Create a valid fixed-amount coupon."""
    return Coupon.objects.create(
        code="FLAT30",
        discount_type="FIXED",
        discount_value=Decimal("30.00"),
        min_order_amount=Decimal("0.00"),
        max_uses=0,
        current_uses=0,
        valid_from=timezone.now() - timedelta(days=10),
        valid_until=timezone.now() + timedelta(days=30),
        is_active=True,
    )

