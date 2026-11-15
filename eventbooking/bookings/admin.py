from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "event",
        "ticket_type",
        "quantity",
        "final_amount",
        "status",
        "booking_date",
    )
    list_filter = ("status", "booking_date")
    search_fields = ("user__username", "event__name")
    readonly_fields = ("booking_date",)

