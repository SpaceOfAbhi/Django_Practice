from django.db import models
from django.conf import settings


class Event(models.Model):
    """Represents an event that users can book tickets for."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    venue = models.CharField(max_length=255)
    event_date = models.DateTimeField()
    total_capacity = models.PositiveIntegerField()
    available_capacity = models.PositiveIntegerField()
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_events",
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["event_date"]

    def __str__(self):
        return f"{self.name} - {self.venue} ({self.event_date.strftime('%Y-%m-%d')})"

    @property
    def is_sold_out(self):
        return self.available_capacity <= 0

    @property
    def tickets_sold(self):
        return self.total_capacity - self.available_capacity


class TicketType(models.Model):
    """Different ticket tiers for an event (e.g., VIP, General, Early Bird)."""

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="ticket_types")
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("event", "name")

    def __str__(self):
        return f"{self.name} - ${self.price} ({self.event.name})"

