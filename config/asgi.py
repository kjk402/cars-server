import asyncio
import os
import threading

import django
from django.core.asgi import get_asgi_application

from train.utils.kafka_listener import kafka_response_listener

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
application = get_asgi_application()


# 비동기 Kafka Listener 실행
def run_kafka_listener():
    asyncio.run(kafka_response_listener())


threading.Thread(target=run_kafka_listener, daemon=True).start()
