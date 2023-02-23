from celery import Celery
from settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery = Celery(
    'src',
    backend=CELERY_RESULT_BACKEND,
    broker=CELERY_BROKER_URL
)

