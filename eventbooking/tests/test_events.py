import pytest
from rest_framework.test import APIClient

from events.services.event_service import get_event_detail, list_active_events


class TestEventList:
    """Tests for listing events."""

    def test_list_active_events_excludes_deleted(
        self, user, future_event, deleted_event
    ):
        """Active event list should not include soft-deleted events."""
        events = list_active_events()
        event_ids = [e.id for e in events]
        assert future_event.id in event_ids
        assert deleted_event.id not in event_ids

    def test_list_events_api(self, user, future_event):
        """GET /api/events/ should return active events."""
        client = APIClient()
        response = client.get("/api/events/")
        assert response.status_code == 200
        assert len(response.data) >= 1


class TestEventDetail:
    """Tests for retrieving event details."""

    def test_get_existing_event(self, user, future_event):
        """Should return event details for a valid event."""
        event = get_event_detail(future_event.id)
        assert event.id == future_event.id
        assert event.name == "Django Conference 2027"

    def test_get_nonexistent_event(self, user):
        """Should raise EventNotFoundError for non-existent event."""
        from eventbooking.exceptions import EventNotFoundError

        with pytest.raises(EventNotFoundError):
            get_event_detail(99999)

    def test_get_deleted_event_should_fail(self, user, deleted_event):
        """
        Should raise EventNotFoundError when retrieving a soft-deleted event.
        Soft-deleted events must not be accessible via the detail endpoint.
        """
        from eventbooking.exceptions import EventNotFoundError

        with pytest.raises(EventNotFoundError):
            get_event_detail(deleted_event.id)

    def test_event_detail_api_returns_404_for_deleted(self, user, deleted_event):
        """GET /api/events/<deleted_id>/ should return 404."""
        client = APIClient()
        response = client.get(f"/api/events/{deleted_event.id}/")
        assert response.status_code == 404

    def test_event_detail_api_success(self, user, future_event, general_ticket):
        """GET /api/events/<id>/ should return full event details."""
        client = APIClient()
        response = client.get(f"/api/events/{future_event.id}/")
        assert response.status_code == 200

