from django.db import models
from django.conf import settings


class Coupon(models.Model):
    """Discount coupon that can be applied to bookings."""

    DISCOUNT_TYPE_CHOICES = [
        ("PERCENTAGE", "Percentage"),
        ("FIXED", "Fixed Amount"),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Minimum order amount required to use this coupon."
    )
    max_uses = models.PositiveIntegerField(
        default=0,
        help_text="Maximum number of times this coupon can be used. 0 means unlimited."
    )
    current_uses = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} ({self.discount_type}: {self.discount_value})"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.valid_until

    @property
    def has_uses_remaining(self):
        if self.max_uses == 0:
            return True  # Unlimited
        return self.current_uses < self.max_uses


class CouponUsage(models.Model):
    """Tracks individual coupon usage by users."""

    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="usages")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coupon_usages",
    )
    booking = models.ForeignKey(
        "bookings.Booking",
        on_delete=models.CASCADE,
        related_name="coupon_usage",
        null=True,
        blank=True,
    )
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("coupon", "user")

    def __str__(self):
        return f"{self.user.username} used {self.coupon.code}"

