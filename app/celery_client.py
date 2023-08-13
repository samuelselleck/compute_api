import uuid;
from celery import Celery
import time
import random
import os
import sys
import signal

REDIS_URL = os.environ["REDIS_URL"]

celery = Celery(
    "api",
    broker=f"{REDIS_URL}/0",
    backend=f"{REDIS_URL}/1",
    worker_prefetch_multiplier=int(os.environ["WORKER_PREFETCH_MULTIPLIER"]),
    task_acks_late=True,
    task_track_started = True
)

def handle_sigterm(*args, **kwargs):
    sys.exit()
signal.signal(signal.SIGTERM, handle_sigterm)

#only runs for worker:
if "WORKER" in os.environ:
    import model
    model_instance = model.Model()

@celery.task
def run_model_prediction(date_start, input_data):
    out = model_instance.predict(input_data)
    return {**out, "date_start": date_start}
    
