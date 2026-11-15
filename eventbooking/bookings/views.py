from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    BookingCreateSerializer,
    BookingCancelSerializer,
    BookingResponseSerializer,
    BookingListSerializer,
)
from .services.booking_service import (
    create_booking,
    cancel_booking,
    get_user_bookings,
    get_booking_detail,
)


class BookingCreateView(APIView):
    """Create a new booking."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = create_booking(
            user=request.user,
            event_id=serializer.validated_data["event_id"],
            ticket_type_id=serializer.validated_data["ticket_type_id"],
            quantity=serializer.validated_data["quantity"],
            coupon_code=serializer.validated_data.get("coupon_code"),
        )

        response_serializer = BookingResponseSerializer(booking)
        return Response(
            {
                "success": True,
                "data": response_serializer.data,
                "message": "Booking created successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class BookingCancelView(APIView):
    """Cancel an existing booking."""

    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        serializer = BookingCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = cancel_booking(
            user=request.user,
            booking_id=booking_id,
            reason=serializer.validated_data.get("reason", ""),
        )

        response_serializer = BookingResponseSerializer(booking)
        return Response(
            {
                "success": True,
                "data": response_serializer.data,
                "message": "Booking cancelled successfully.",
            },
            status=status.HTTP_200_OK,
        )


class BookingListView(APIView):
    """List all bookings for the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = get_user_bookings(request.user)
        serializer = BookingListSerializer(bookings, many=True)
        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class BookingDetailView(APIView):
    """Get details of a specific booking."""

    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):
        booking = get_booking_detail(request.user, booking_id)
        serializer = BookingResponseSerializer(booking)
        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

