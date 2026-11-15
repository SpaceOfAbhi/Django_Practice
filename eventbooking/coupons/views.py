from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import CouponValidateSerializer, CouponResponseSerializer
from .services.coupon_service import validate_and_apply_coupon, get_coupon_details
from bookings.utils.pricing import calculate_discount


class CouponValidateView(APIView):
    """Validate a coupon and return discount information."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        coupon, discount_amount = validate_and_apply_coupon(
            coupon_code=serializer.validated_data["code"],
            user=request.user,
            order_amount=serializer.validated_data["order_amount"],
        )

        coupon_serializer = CouponResponseSerializer(coupon)
        return Response(
            {
                "success": True,
                "data": {
                    "coupon": coupon_serializer.data,
                    "discount_amount": str(discount_amount),
                },
                "message": "Coupon is valid.",
            },
            status=status.HTTP_200_OK,
        )


class CouponDetailView(APIView):
    """Get details of a coupon by code."""

    permission_classes = [IsAuthenticated]

    def get(self, request, code):
        coupon = get_coupon_details(code)
        serializer = CouponResponseSerializer(coupon)
        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

