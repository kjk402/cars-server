# views.py
import asyncio
import time
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils.kafka_config import send_predict_request_async, wait_for_response_async


@swagger_auto_schema(
    method="post",
    operation_summary="차량 가격 예측 요청",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["engineSize", "year", "mileage", "fuelType"],
        properties={
            "engineSize": openapi.Schema(type=openapi.TYPE_NUMBER),
            "year": openapi.Schema(type=openapi.TYPE_INTEGER),
            "mileage": openapi.Schema(type=openapi.TYPE_INTEGER),
            "fuelType": openapi.Schema(type=openapi.TYPE_STRING),
            "brand": openapi.Schema(type=openapi.TYPE_STRING),
            "model": openapi.Schema(type=openapi.TYPE_STRING),
        },
    )
)
@api_view(["POST"])
def predict_car_price_view(request):
    start_time = time.time()
    try:
        input_data = request.data

        # ✅ 비동기 함수 실행을 asyncio.run 대신 이벤트 루프로 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        request_id = loop.run_until_complete(send_predict_request_async(input_data))
        response_data = loop.run_until_complete(wait_for_response_async(request_id, timeout=10))

        loop.close()

        if not response_data:
            return Response(
                {"error": "예측 응답 타임아웃"},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        end_time = time.time()  # 요청 종료 시간 기록
        print(f"요청 처리 시간: {end_time - start_time:.4f} 초")  # 처리 시간 출력

        return Response(response_data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)