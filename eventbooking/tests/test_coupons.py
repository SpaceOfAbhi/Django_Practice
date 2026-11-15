import pytest
from decimal import Decimal

from rest_framework.test import APIClient

from coupons.models import CouponUsage
from coupons.services.coupon_service import validate_and_apply_coupon
from eventbooking.exceptions import (
    CouponNotFoundError,
    CouponExpiredError,
    CouponUsageLimitError,
    CouponMinimumAmountError,
    CouponAlreadyUsedError,
)


# ===========================================================================
# COUPON VALIDATION SUCCESS TESTS
# ===========================================================================

class TestCouponValidationSuccess:
    """Tests for successful coupon validation."""

    def test_validate_percentage_coupon(self, user, valid_coupon):
        """Should correctly calculate percentage discount."""
        coupon, discount = validate_and_apply_coupon(
            coupon_code="SAVE20",
            user=user,
            order_amount=Decimal("200.00"),
        )
        assert coupon.id == valid_coupon.id
        assert discount == Decimal("40.00")  # 20% of 200

    def test_validate_fixed_coupon(self, user, fixed_coupon):
        """Should correctly calculate fixed discount."""
        coupon, discount = validate_and_apply_coupon(
            coupon_code="FLAT30",
            user=user,
            order_amount=Decimal("100.00"),
        )
        assert coupon.id == fixed_coupon.id
        assert discount == Decimal("30.00")

    def test_coupon_increments_usage(self, user, valid_coupon):
        """Validating a coupon should increment its usage count."""
        initial_uses = valid_coupon.current_uses
        validate_and_apply_coupon(
            coupon_code="SAVE20",
            user=user,
            order_amount=Decimal("100.00"),
        )
        valid_coupon.refresh_from_db()
        assert valid_coupon.current_uses == initial_uses + 1


# ===========================================================================
# COUPON VALIDATION FAILURE TESTS
# ===========================================================================

class TestCouponValidationFailures:
    """Tests for coupon validation failures."""

    def test_nonexistent_coupon(self, user):
        """Should raise CouponNotFoundError for non-existent coupon code."""
        with pytest.raises(CouponNotFoundError):
            validate_and_apply_coupon(
                coupon_code="DOESNOTEXIST",
                user=user,
                order_amount=Decimal("100.00"),
            )

    def test_deleted_coupon(self, user, deleted_coupon):
        """
        Should raise CouponNotFoundError for a soft-deleted coupon.
        Deleted coupons must not be usable.
        """
        with pytest.raises(CouponNotFoundError):
            validate_and_apply_coupon(
                coupon_code="DELETED",
                user=user,
                order_amount=Decimal("100.00"),
            )

    def test_expired_coupon(self, user, expired_coupon):
        """
        Should raise CouponExpiredError for a coupon past its valid_until date.
        """
        with pytest.raises(CouponExpiredError):
            validate_and_apply_coupon(
                coupon_code="EXPIRED50",
                user=user,
                order_amount=Decimal("200.00"),
            )

    def test_inactive_coupon(self, user, inactive_coupon):
        """
        Should raise CouponExpiredError for an inactive coupon.
        Inactive coupons are treated as expired from a user perspective.
        """
        with pytest.raises(CouponExpiredError):
            validate_and_apply_coupon(
                coupon_code="INACTIVE",
                user=user,
                order_amount=Decimal("100.00"),
            )

    def test_maxed_out_coupon(self, user, maxed_out_coupon):
        """
        Should raise CouponUsageLimitError when coupon has reached
        its maximum usage count.
        """
        with pytest.raises(CouponUsageLimitError):
            validate_and_apply_coupon(
                coupon_code="MAXED",
                user=user,
                order_amount=Decimal("100.00"),
            )

    def test_coupon_below_minimum_amount(self, user, high_minimum_coupon):
        """
        Should raise CouponMinimumAmountError when order amount is
        below the coupon's minimum requirement.
        """
        with pytest.raises(CouponMinimumAmountError):
            validate_and_apply_coupon(
                coupon_code="BIGORDER",
                user=user,
                order_amount=Decimal("100.00"),  # Minimum is 500
            )

    def test_coupon_already_used_by_user(self, user, valid_coupon):
        """
        Should raise CouponAlreadyUsedError when user has already
        used this coupon (one use per user).
        """
        # Record that this user already used the coupon
        CouponUsage.objects.create(coupon=valid_coupon, user=user)

        with pytest.raises(CouponAlreadyUsedError):
            validate_and_apply_coupon(
                coupon_code="SAVE20",
                user=user,
                order_amount=Decimal("100.00"),
            )

    def test_deleted_coupon_does_not_increment_usage(self, user, deleted_coupon):
        """Usage count should not change when validation fails."""
        initial_uses = deleted_coupon.current_uses
        with pytest.raises(CouponNotFoundError):
            validate_and_apply_coupon(
                coupon_code="DELETED",
                user=user,
                order_amount=Decimal("100.00"),
            )
        deleted_coupon.refresh_from_db()
        assert deleted_coupon.current_uses == initial_uses

    def test_expired_coupon_does_not_increment_usage(self, user, expired_coupon):
        """Usage count should not change when validation fails."""
        initial_uses = expired_coupon.current_uses
        with pytest.raises(CouponExpiredError):
            validate_and_apply_coupon(
                coupon_code="EXPIRED50",
                user=user,
                order_amount=Decimal("200.00"),
            )
        expired_coupon.refresh_from_db()
        assert expired_coupon.current_uses == initial_uses


# ===========================================================================
# COUPON API TESTS
# ===========================================================================

class TestCouponAPI:
    """Tests for coupon API endpoints."""

    def test_validate_coupon_api_success(self, user, valid_coupon):
        """POST /api/coupons/validate/ should validate a coupon."""
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            "/api/coupons/validate/",
            {"code": "SAVE20", "order_amount": "200.00"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["success"] is True
        assert "discount_amount" in response.data["data"]

    def test_validate_expired_coupon_api(self, user, expired_coupon):
        """POST /api/coupons/validate/ with expired coupon should return 400."""
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            "/api/coupons/validate/",
            {"code": "EXPIRED50", "order_amount": "200.00"},
            format="json",
        )
        assert response.status_code == 400

    def test_validate_nonexistent_coupon_api(self, user):
        """POST /api/coupons/validate/ with bad code should return 404."""
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            "/api/coupons/validate/",
            {"code": "FAKECODE", "order_amount": "100.00"},
            format="json",
        )
        assert response.status_code == 404

    def test_coupon_api_unauthenticated(self):
        """POST /api/coupons/validate/ without auth should return 403."""
        client = APIClient()
        response = client.post(
            "/api/coupons/validate/",
            {"code": "SAVE20", "order_amount": "100.00"},
            format="json",
        )
        assert response.status_code == 403

