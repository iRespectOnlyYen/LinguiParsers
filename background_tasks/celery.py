from celery import Celery
from core import settings


celery = Celery(
    "dictionary_tasks",
    broker=settings.REDIS_URL,
    include=["background_tasks.tasks"],
)