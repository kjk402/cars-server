# urls.py
from django.urls import path
from .views import predict_car_price_view

urlpatterns = [
    path("predict/", predict_car_price_view, name="predict"),
]
