#!/bin/bash

#make sure "docker" commands set up
#containers in internal minikube registry
eval $(minikube -p minikube docker-env)

#build local images
docker build -f app/Dockerfile.api -t api app
docker build -f app/Dockerfile.celery-worker -t celery_worker app

#create namespaces
kubectl create namespace api
kubectl create namespace model

#configmap (global)
kubectl apply -f configmap.yaml -n api
kubectl apply -f configmap.yaml -n model

#deployments/services
kubectl apply -f redis.yaml -n api
kubectl apply -f api.yaml -n api
kubectl apply -f celery-worker.yaml -n model

#install keda (see https://keda.sh/)
kubectl apply --server-side -f https://github.com/kedacore/keda/releases/download/v2.11.0/keda-2.11.0.yaml

#keda celery-worker scaler
kubectl apply -f keda-scaleobject.yaml -n model

#restart all pods
kubectl delete pods --all -n api
kubectl delete pods --all -n model
