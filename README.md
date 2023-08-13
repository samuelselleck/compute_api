
# Auto Scaling Kubernetes API

This project implements an API endpoint for machine learning model evaluation
or other compute limited tasks where autoscaling of worker pods is desired.

# Software Stack

* Kubernetes
* Redis
* Celery (https://docs.celeryq.dev/en/stable/index.html)
* FastAPI (https://fastapi.tiangolo.com/)

# Model Inference

The number of celery worker pods processing incoming requests are automatically scaled based on the number of requests currently in queue. The queue jobs are automatically redirected to running pods that runs inference on the following toy model:

```python
class Model:
    def __init__(self):
        time.sleep(self.setup_time())
        self.uuid = str(uuid.uuid4())

    def predict(self, input: str):
        time.sleep(self.predict_time())
        output = f"""\
		model inference on instance {self.uuid}\
		with input {input} was successfull!
		"""
        return {"output": output, "input": input}

    def setup_time(self):
        return 30

    def predict_time(self):
        return 5

```
# Endpoints

The api has the following endpoints:

* post to `https://localhost:8002/push?input=<your-input-string>` returns unique ID associated with job
* get to `https://localhost:8002//status/{id}` returns json body with status of the job
* get to `https://localhost:8002//data/{id}` returns json body  with computed output and request latency

# Installation

### Prerequisites.
You need to have **minikube**, **kubectl** and **docker** installed. I've been developing on a M1 macbook, but I don't think I've used any platform specific dependencies. If you have any setup problems just shoot me an email.

### Setup
To run the project, execute the following in the root directory:

```
minikube start
./setup_cluster.sh
minikube tunnel
```
and keep the process running in the background.

The api should then be available through https://localhost:8002.

If you want to change the model.py file, replace the file in `app/model.py` and rerun `setup_cluster.sh`.

### Tests and Parameter Experiments

You need to install `kubernetes` and `matplotlib` to run the tests.

* integration tests: `python tests/integration_tests.py`
* parameter experiments (results are cached in `tests/experiment_outputs`): `python tests/parameter_experiments.py`

Resource efficiency wise, the current setup reboots the entire minikube container on every test run. This is probably a bit much.

# Things I'd like to improve

The current pod scaling schema using KEDA autoscaling based on Redis list length
is not sufficient when the startup time is large. A custom pod scaler that takes
startup time into account would substantially improve scaling properties.
