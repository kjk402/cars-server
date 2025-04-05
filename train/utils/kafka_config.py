import json
import uuid
from kafka import KafkaProducer, KafkaConsumer
from config import settings

producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    request_timeout_ms=2000,  # 요청 타임아웃 5초
    max_block_ms=2000
)


def send_predict_request(payload):
    request_id = str(uuid.uuid4())
    payload["request_id"] = request_id  # <- 여기에 넣어줘야 함
    producer.send(settings.PREDICT_REQUEST_TOPIC, payload)
    producer.flush()
    return request_id


def wait_for_response(request_id, timeout=10):
    consumer = KafkaConsumer(
        settings.PREDICT_RESPONSE_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='django_response_group'
    )

    for message in consumer:
        data = message.value
        if data.get("request_id") == request_id:
            consumer.close()
            return data
    return None