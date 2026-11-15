from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import Event
from .serializers import EventListSerializer, EventDetailSerializer
from .services.event_service import get_event_detail, list_active_events


class EventListView(generics.ListAPIView):
    """List all active events."""

    serializer_class = EventListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return list_active_events()


class EventDetailView(generics.RetrieveAPIView):
    """Retrieve details for a specific event."""

    serializer_class = EventDetailSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        event_id = self.kwargs["pk"]
        return get_event_detail(event_id)

