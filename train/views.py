import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class PredictCarPriceAPIView(APIView):

    @swagger_auto_schema(
        operation_summary="차량 가격 예측 요청",
        operation_description="차량의 연식, 배기량, 주행거리, 연료 타입, 브랜드, 모델을 기반으로 가격 예측을 수행합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["engineSize", "year", "mileage", "fuelType"],
            properties={
                "engineSize": openapi.Schema(type=openapi.TYPE_NUMBER, description="배기량 (예: 2.0)"),
                "year": openapi.Schema(type=openapi.TYPE_INTEGER, description="연식 (예: 2019)"),
                "mileage": openapi.Schema(type=openapi.TYPE_INTEGER, description="주행거리 (예: 30000)"),
                "fuelType": openapi.Schema(type=openapi.TYPE_STRING, description="연료 타입 (예: Petrol)"),
                "brand": openapi.Schema(type=openapi.TYPE_STRING, description="브랜드 (예: audi)", example="audi"),
                "model": openapi.Schema(type=openapi.TYPE_STRING, description="모델 (예: A3)", example="A3"),
            },
            example={
                "engineSize": 3.0,
                "year": 2017,
                "mileage": 21000,
                "fuelType": "Diesel",
                "brand": "audi",
                "model": " A7"
            }
        ),
        responses={
            200: openapi.Response(
                description="예측 결과 및 그래프 base64",
                examples={
                    "application/json": {
                        "predicted_price": 16800,
                        "image_base64": "<base64_encoded_string>"
                    }
                }
            ),
            500: "서버 에러"
        }
    )
    def post(self, request):
        try:
            input_data = request.data
            res = requests.post("http://localhost:8001/predict", json=input_data)
            res.raise_for_status()
            return Response(res.json())
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
