# urls.py
from django.urls import path

from .views import predict_car_price_view, health_check_kafka

urlpatterns = [
    path("predict/", predict_car_price_view, name="predict"),
    path("health/", health_check_kafka),
]
