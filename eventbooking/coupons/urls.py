from django.urls import path
from . import views

urlpatterns = [
    path("validate/", views.CouponValidateView.as_view(), name="coupon-validate"),
    path("<str:code>/", views.CouponDetailView.as_view(), name="coupon-detail"),
]

