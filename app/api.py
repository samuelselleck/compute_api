from datetime import datetime
from fastapi import FastAPI, HTTPException
import celery
import celery_client

app = FastAPI()


@app.post("/push")
async def push_data(input: str = ""):
    date_start  = datetime.now();
    if not input:
        raise HTTPException(status_code=400, detail="empty input")
    result = celery_client.run_model_prediction.apply_async(
        [date_start, input],
    )
    result.backend.store_result(result.task_id, None, "SENT")
    return {"id": result.task_id }


@app.get("/status/{id}")
async def get_job_status(id: str):
    result = celery_client.run_model_prediction.AsyncResult(id)
    if result.state == "PENDING":
        raise HTTPException(status_code=404, detail="job not found")
    codes = {
        "SENT": "queued",
        "STARTED": "processing",
        "SUCCESS": "finished",
    }
    status  = codes.get(result.state, "error processing job: " + result.state)
    return {"status": status}


@app.get("/data/{id}")
async def get_job_data(id: str):
    result = celery_client.run_model_prediction.AsyncResult(id)
    if result.state != "SUCCESS":
        raise HTTPException(status_code=404, detail="job result not found")
    output = result.get(timeout=5)
    date_start = output["date_start"]
    del output["date_start"]
    delta = result.date_done - date_start
    return {
        **output,
        "latency": delta.total_seconds(),
    }
