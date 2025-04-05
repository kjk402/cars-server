import json
import uuid

from aiokafka import AIOKafkaProducer

from config import settings

producer = None


async def init_producer():
    global producer
    if not producer:
        producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await producer.start()


async def send_predict_request_async(payload):
    await init_producer()

    request_id = str(uuid.uuid4())
    payload["request_id"] = request_id
    await producer.send(settings.PREDICT_REQUEST_TOPIC, payload)
    return request_id
