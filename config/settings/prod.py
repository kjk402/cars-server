# config/settings/prod.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True

ELASTICSEARCH_HOST = "http://localhost:9200"

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'http://localhost:9200'  # Elasticsearch 서버 주소
    }
}


KAFKA_BOOTSTRAP_SERVERS = "172.27.152.112:9092"