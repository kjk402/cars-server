# config/asgi.py
import asyncio
import os
import threading

import django
from django.core.asgi import get_asgi_application

from train.utils.kafka_listener import kafka_response_listener, kafka_health_response_listener

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()
application = get_asgi_application()

listener_started = False

def run_kafka_listener():
    global listener_started
    if listener_started:
        print("⚠️ Kafka listener already started, skipping")
        return

    listener_started = True
    print("🟢 Kafka listener started")

    async def start_kafka_listeners():
        await asyncio.gather(
            kafka_response_listener(),
            kafka_health_response_listener(),
        )

    threading.Thread(target=lambda: asyncio.run(start_kafka_listeners()), daemon=True).start()

if os.environ.get("RUN_MAIN", None) != "true":
    run_kafka_listener()
