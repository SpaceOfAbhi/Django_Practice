from decimal import Decimal


def calculate_total_price(ticket_price, quantity):
    """Calculate the total price before any discounts."""
    return Decimal(str(ticket_price)) * quantity


def calculate_discount(total_amount, discount_type, discount_value):
    """
    Calculate the discount amount based on coupon type.

    Args:
        total_amount: The total order amount before discount.
        discount_type: Either 'PERCENTAGE' or 'FIXED'.
        discount_value: The discount value (percentage or fixed amount).

    Returns:
        Decimal: The discount amount.
    """
    if discount_type == "PERCENTAGE":
        discount = (Decimal(str(discount_value)) / Decimal("100")) * total_amount
        return min(discount, total_amount)  # Discount cannot exceed total
    elif discount_type == "FIXED":
        return min(Decimal(str(discount_value)), total_amount)  # Discount cannot exceed total
    return Decimal("0")


def calculate_final_amount(total_amount, discount_amount):
    """Calculate the final amount after applying discount."""
    final = total_amount - discount_amount
    return max(final, Decimal("0"))  # Final amount cannot be negative


def calculate_refund_amount(booking):
    """
    Calculate refund amount for a cancelled booking.

    Business Rule: Full refund if cancelled more than 48 hours before event,
    50% refund if cancelled between 24 and 48 hours before event.
    No refund within 24 hours (but cancellation should be blocked anyway).
    """
    from django.utils import timezone
    import datetime

    hours_until_event = (booking.event.event_date - timezone.now()).total_seconds() / 3600

    if hours_until_event > 48:
        return booking.final_amount
    elif hours_until_event > 24:
        return booking.final_amount * Decimal("0.5")
    else:
        return Decimal("0")

