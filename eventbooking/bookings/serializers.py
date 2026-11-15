from rest_framework import serializers
from .models import Booking


class BookingCreateSerializer(serializers.Serializer):
    """Serializer for creating a new booking."""

    event_id = serializers.IntegerField()
    ticket_type_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    coupon_code = serializers.CharField(required=False, allow_blank=True, default="")


class BookingCancelSerializer(serializers.Serializer):
    """Serializer for cancelling a booking."""

    reason = serializers.CharField(required=False, allow_blank=True, default="")


class BookingResponseSerializer(serializers.ModelSerializer):
    """Serializer for booking response data."""

    event_name = serializers.CharField(source="event.name", read_only=True)
    ticket_type_name = serializers.CharField(source="ticket_type.name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "username",
            "event_name",
            "ticket_type_name",
            "quantity",
            "total_amount",
            "discount_amount",
            "final_amount",
            "status",
            "booking_date",
            "cancelled_at",
            "cancellation_reason",
        ]


class BookingListSerializer(serializers.ModelSerializer):
    """Serializer for listing bookings."""

    event_name = serializers.CharField(source="event.name", read_only=True)
    ticket_type_name = serializers.CharField(source="ticket_type.name", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "event_name",
            "ticket_type_name",
            "quantity",
            "final_amount",
            "status",
            "booking_date",
        ]

