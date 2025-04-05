import time
from asgiref.sync import async_to_sync
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .kafka_response_map import response_map
from .utils.kafka_config import send_predict_request_async


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
        request_id = async_to_sync(send_predict_request_async)(input_data)

        for _ in range(100):
            if request_id in response_map:
                end_time = time.time()  # 응답 받은 시간 기록
                print(f"요청 처리 시간: {end_time - start_time:.4f} 초")  # 처리 시간 출력
                return Response(response_map.pop(request_id))
            time.sleep(0.1)

        return Response(
            {"error": "예측 응답 타임아웃"},
            status=status.HTTP_504_GATEWAY_TIMEOUT
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
