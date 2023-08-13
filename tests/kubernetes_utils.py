
import asyncio
import time
import datetime
import matplotlib.pyplot as plt
import random
from kubernetes import client, config


def _get_deployment_replicas(namespace, deployment):
    config.load_kube_config()
    api_instance = client.AppsV1Api()
    deployment = api_instance.read_namespaced_deployment(deployment, namespace)
    return deployment.status.replicas

async def replicas_over_duration(namespace, deployment, duration, sample_interval):
    config.load_kube_config()
    replica_counts = []
    timestamps = []
    start_time = time.time()
    elapsed = 0
    while elapsed < duration:
        elapsed = time.time() - start_time
        replicas = _get_deployment_replicas("model", "celery-worker")
        replica_counts.append(replicas)
        timestamps.append(elapsed)
        await asyncio.sleep(sample_interval)

    return timestamps, replica_counts

async def delete_random_pods(duration, interval, namespace, deployment):
    config.load_kube_config()
    v1 = client.CoreV1Api()

    start_time = time.time()
    elapsed = 0
    while elapsed < duration:
        elapsed = time.time() - start_time

        pods = v1.list_namespaced_pod(namespace=namespace, label_selector=f"app={deployment}")
        if pods.items:
            random_pod = random.choice(pods.items)
            pod_name = random_pod.metadata.name
            v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
        await asyncio.sleep(interval)

