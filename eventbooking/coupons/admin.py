from django.contrib import admin
from .models import Coupon, CouponUsage


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "discount_value",
        "max_uses",
        "current_uses",
        "valid_from",
        "valid_until",
        "is_active",
        "is_deleted",
    )
    list_filter = ("is_active", "is_deleted", "discount_type")
    search_fields = ("code",)


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ("coupon", "user", "booking", "used_at")
    list_filter = ("used_at",)

