from .base import *
import environ

env = environ.Env(
    DEBUG=(bool, True),
    CORS_ALLOW_ALL_ORIGINS=(bool, True)
)
environ.Env.read_env(".env.dev")

DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(",")
CORS_ALLOW_ALL_ORIGINS = env("CORS_ALLOW_ALL_ORIGINS")

ELASTICSEARCH_HOST = env("ELASTICSEARCH_HOST")

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': ELASTICSEARCH_HOST
    }
}

KAFKA_BOOTSTRAP_SERVERS = env("KAFKA_BOOTSTRAP_SERVERS")
