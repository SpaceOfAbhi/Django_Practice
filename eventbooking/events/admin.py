from django.contrib import admin
from .models import Event, TicketType


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "venue", "event_date", "total_capacity", "available_capacity", "is_deleted")
    list_filter = ("is_deleted", "event_date")
    search_fields = ("name", "venue")


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "event", "price", "quantity_available", "is_active")
    list_filter = ("is_active",)

