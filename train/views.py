import requests
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils.kafka_config import send_predict_request, wait_for_response
from .utils.kafka_config import producer

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
        start_time = time.time()
        try:
            input_data = request.data

            # ✅ Kafka 요청 보내기
            request_id = send_predict_request(input_data)

            # ✅ Kafka 응답 대기
            response = wait_for_response(request_id, timeout=10)
            if not response:
                return Response({"error": "예측 응답 타임아웃"}, status=status.HTTP_504_GATEWAY_TIMEOUT)

            end_time = time.time()  # 요청 종료 시간 기록
            print(f"요청 처리 시간: {end_time - start_time:.4f} 초")  # 처리 시간 출력

            return Response(response)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class KafkaTestSendAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="Kafka 테스트 메시지 전송",
        operation_description="Kafka에 테스트 메시지를 전송합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(type=openapi.TYPE_STRING, description="보낼 메시지")
            },
            required=["message"],
            example={"message": "Hello Kafka"}
        ),
        responses={200: openapi.Response(description="메시지 전송 성공")}
    )
    def post(self, request):
        try:
            message = request.data.get("message", "default message")
            payload = {"test_message": message}
            producer.send("111car-predict-request", payload)
            producer.flush()
            return Response({"status": "sent", "payload": payload})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)