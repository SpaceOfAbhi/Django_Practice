from decimal import Decimal

from coupons.models import Coupon, CouponUsage
from bookings.utils.pricing import calculate_discount
from eventbooking.exceptions import (
    CouponNotFoundError,
    CouponExpiredError,
    CouponUsageLimitError,
    CouponMinimumAmountError,
    CouponAlreadyUsedError,
)


def validate_and_apply_coupon(coupon_code, user, order_amount):
    """
    Validate a coupon and calculate the discount amount.

    This function should:
    1. Check if the coupon exists and is not soft-deleted.
    2. Check if the coupon is active.
    3. Check if the coupon has not expired.
    4. Check if the coupon has remaining uses.
    5. Check if the user has already used this coupon.
    6. Check if the order meets the minimum amount requirement.
    7. Calculate and return the discount amount.

    Args:
        coupon_code: The coupon code string.
        user: The authenticated user.
        order_amount: The total order amount before discount.

    Returns:
        Tuple of (Coupon instance, discount_amount as Decimal).

    Raises:
        CouponNotFoundError: If coupon doesn't exist or is deleted.
        CouponExpiredError: If coupon has expired.
        CouponUsageLimitError: If coupon usage limit reached.
        CouponAlreadyUsedError: If user already used this coupon.
        CouponMinimumAmountError: If order doesn't meet minimum.
    """
    # Step 1: Fetch the coupon
    try:
        coupon = Coupon.objects.get(code=coupon_code)
    except Coupon.DoesNotExist:
        raise CouponNotFoundError()

    # Step 2: Calculate discount
    discount_amount = calculate_discount(
        total_amount=Decimal(str(order_amount)),
        discount_type=coupon.discount_type,
        discount_value=coupon.discount_value,
    )

    # Step 3: Update coupon usage count
    coupon.current_uses += 1
    coupon.save()

    return coupon, discount_amount


def get_coupon_details(coupon_code):
    """
    Get details of a specific coupon.

    Args:
        coupon_code: The coupon code string.

    Returns:
        Coupon instance.

    Raises:
        CouponNotFoundError: If coupon doesn't exist.
    """
    try:
        coupon = Coupon.objects.get(code=coupon_code)
    except Coupon.DoesNotExist:
        raise CouponNotFoundError()

    return coupon

