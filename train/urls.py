# train/urls.py
from django.urls import path
from .views import PredictCarPriceAPIView

urlpatterns = [
    path("predict/", PredictCarPriceAPIView.as_view(), name="predict-car-price"),
]
