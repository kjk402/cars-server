import asyncio
import json
import uuid

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

from config import settings


async def send_predict_request_async(payload):
    request_id = str(uuid.uuid4())
    payload["request_id"] = request_id

    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    await producer.start()
    try:
        await producer.send(settings.PREDICT_REQUEST_TOPIC, payload)
    finally:
        await producer.stop()

    return request_id


async def wait_for_response_async(request_id, timeout=10):
    consumer = AIOKafkaConsumer(
        settings.PREDICT_RESPONSE_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=False,
        group_id="django_response_group",
        # fetch_max_bytes=1048576,  # 1MB
        # max_partition_fetch_bytes=1048576,  # 1MB
        # fetch_max_wait_ms=11,
        # max_poll_records=11000,
    )
    await consumer.start()
    try:
        start_time = asyncio.get_event_loop().time()
        async for message in consumer:
            data = message.value
            if data.get("request_id") == request_id:
                return data
            if asyncio.get_event_loop().time() - start_time > timeout:
                break
    finally:
        await consumer.stop()
    return None

