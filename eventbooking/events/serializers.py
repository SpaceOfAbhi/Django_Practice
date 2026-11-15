from rest_framework import serializers
from .models import Event, TicketType


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ["id", "name", "price", "quantity_available", "is_active"]


class EventListSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source="organizer.get_full_name", read_only=True)
    tickets_sold = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "venue",
            "event_date",
            "total_capacity",
            "available_capacity",
            "tickets_sold",
            "organizer_name",
            "is_sold_out",
        ]


class EventDetailSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source="organizer.get_full_name", read_only=True)
    ticket_types = TicketTypeSerializer(many=True, read_only=True)
    tickets_sold = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "description",
            "venue",
            "event_date",
            "total_capacity",
            "available_capacity",
            "tickets_sold",
            "organizer_name",
            "ticket_types",
            "is_sold_out",
            "created_at",
            "updated_at",
        ]

