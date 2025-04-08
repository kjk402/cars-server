import json
import uuid
from aiokafka import AIOKafkaConsumer

from django.conf import settings
from train.kafka_response_map import response_map


async def kafka_response_listener():
    consumer = AIOKafkaConsumer(
        settings.PREDICT_RESPONSE_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        group_id="django_predict_response_group",
        auto_offset_reset="latest",
        enable_auto_commit=True
    )

    await consumer.start()
    try:
        async for message in consumer:
            data = message.value
            request_id = data.get("request_id")
            if request_id:
                response_map[request_id] = data
    except Exception as e:
        print("❌ Kafka Listener Error:", e)
    finally:
        await consumer.stop()


async def kafka_health_response_listener():
    instance_id = str(uuid.uuid4())[:8]
    consumer = AIOKafkaConsumer(
        settings.HEALTH_CHECK_RESPONSE_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        group_id="django_health_response_group",
        auto_offset_reset="latest",
        enable_auto_commit=True
    )

    await consumer.start()
    try:
        async for message in consumer:
            data = message.value
            request_id = data.get("request_id")
            if request_id:
                response_map[request_id] = data
    except Exception as e:
        print("❌ Kafka Listener Error:", e)
    finally:
        await consumer.stop()
