from rest_framework import serializers
from .models import Coupon


class CouponValidateSerializer(serializers.Serializer):
    """Serializer for validating a coupon."""

    code = serializers.CharField(max_length=50)
    order_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class CouponResponseSerializer(serializers.ModelSerializer):
    """Serializer for coupon response data."""

    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "discount_type",
            "discount_value",
            "min_order_amount",
            "valid_from",
            "valid_until",
            "is_active",
        ]

