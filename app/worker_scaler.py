import asyncio
import math
import requests
from fastapi import FastAPI
from statistics import mean
from redis import StrictRedis
import uvicorn
import time

app = FastAPI()
r_client = StrictRedis(host='redis', port=6379, decode_responses=True)
#how often rescaling happens
UPDATE_INTERVAL = 10
#how many seconds (excluding startup time) it should take to bring queue to 0
QUEUE_BACKUP_MAX_TIME = 10
MARGIN_FREQ = 1.1
MARGIN_QUEUE = 1.1

metrics: dict[str, dict[str, float]] = {}

m_lock = asyncio.Lock()

@app.post("/metricupdate/{id}")
async def metric_update(id: str, freq: float, eval: float):
	async with m_lock:
		print(f"recieved metrics from \"{id}\": freq = {freq}, eval_time = {eval}")
		global metrics
		metrics[id] = {"freq": freq, "eval_time": eval, "timestamp": time.time()}

async def worker_scaler():
	global metrics
	while True:

		async with m_lock:
			metrics = {k:v for k, v in metrics.items() if v["timestamp"] < time.time() + 60}
		
			request_freq = sum([m["freq"] for m in metrics.values()])
			eval_time = mean([m["eval_time"] for m in metrics.values()])

		queue_length = r_client.llen('celery')
		#number of workers needed based on
		#eval average + requests per sec
		n_workers_req = request_freq*eval_time*MARGIN_FREQ

		#number of workers needed to reduce
		#queue length wthin QUEUE_BACKUP_MAX_TIME
		n_workers_q_length = queue_length*eval_time/QUEUE_BACKUP_MAX_TIME*MARGIN_QUEUE

		#total
		n_workers = math.ceil(n_workers_req + n_workers_q_length)

		print(f"scaling depoyment to {n_workers} based on metrics {metrics} and list length {queue_length}")

		#TODO scale the celery-worker deployment accordingly
		
		await asyncio.sleep(UPDATE_INTERVAL)
	pass



if __name__ == "__main__":
	asyncio.run(worker_scaler())
	uvicorn.run(app, host="0.0.0.0", port=4242)
