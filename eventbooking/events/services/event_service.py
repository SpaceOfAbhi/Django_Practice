from events.models import Event
from eventbooking.exceptions import EventNotFoundError


def get_event_detail(event_id):
    """
    Retrieve detailed information about a specific event.

    Args:
        event_id: The primary key of the event.

    Returns:
        Event instance.

    Raises:
        EventNotFoundError: If the event does not exist.
    """
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        raise EventNotFoundError()

    return event


def list_active_events():
    """
    List all active (non-deleted) events.

    Returns:
        QuerySet of active events.
    """
    return Event.objects.filter(is_deleted=False).select_related("organizer")

