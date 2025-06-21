# Full-Stack Observability with OpenTelemetry in Kubernetes

Welcome to the **Observability Blueprint** — a hands-on project that demonstrates **complete observability** of a machine learning application deployed in Kubernetes, using open-source tools like **OpenTelemetry**, **Prometheus**, **Jaeger**, **Loki**, and **Grafana**.

This repository walks you through instrumenting a FastAPI app, deploying it on Kubernetes, and observing every layer — from app to cluster.

## Project Structure

```text
├── app/
│   ├── app.py                      # FastAPI app with OTEL instrumentation
│   ├── train_model.py              # Linear Regression ML model trainer
│   ├── requirements.txt
|   ├── .dockerignore
│   └── Dockerfile
│
├── k8s/
│   ├── app.yaml                    # Deployment and Service for the app
│   ├── jaeger.yaml
│   ├── prometheus.yaml
│   ├── loki.yaml
│   └── grafana.yaml
|
├── otel/
│   ├── otel-collector-agent-*.yaml    # Deployment and Service for OTel
│   ├── otel-collector-gateway-*.yaml
```
---

## Getting Started

> You need Docker, Python 3.10+, and a running Kubernetes cluster (e.g., minikube).

### Step 1: Run the App Locally

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip3 install --upgrade pip

# Install dependencies
pip3 install -r requirements.txt

# Train model
python3 train_model.py

# Run API
uvicorn app:app --host 0.0.0.0 --port 8000
```

Test the API:

```bash
curl -i 'http://127.0.0.1:8000/'
curl -i -X POST 'http://127.0.0.1:8000/predict/' -H "Content-Type: application/json" -d '{"features": [1500]}'
```

### Step 2: Build & Run Docker Image

```bash
docker build -t house-price-predictor:v2 .
docker run -d -p 8000:8000 --name house-price-predictor house-price-predictor:v2
```

---

## Kubernetes Setup

### 1. Deploy the App

```bash
kubectl create namespace mlapp
kubectl -n mlapp apply -f app.yaml
kubectl -n mlapp logs -f -l app=house-price-service

# Test service inside cluster
API_ENDPOINT_IP=$(kubectl -n mlapp get svc -l app=house-price-service -o json | jq -r '.items[].spec.clusterIP')

curl -X POST "http://${API_ENDPOINT_IP}:80/predict/" \
  -H "Content-Type: application/json" \
  -d '{"features": [1200]}'
```

### 2. Deploy OTEL Collector Agent

```bash
kubectl create namespace observability
kubectl -n observability apply -f otel-collector-agent-configmap.yaml -f otel-collector-agent-service.yaml -f otel-collector-agent-daemonset.yaml
kubectl -n observability get all -l app=otel-collector-agent
```

### 3. Deploy Jaeger

```bash
kubectl -n observability apply -f jaeger.yaml
kubectl -n observability get all -l app=jaeger
kubectl -n observability port-forward svc/jaeger 16686:16686
```

### 4. Deploy Prometheus

```bash
kubectl -n observability apply -f prometheus.yaml
kubectl -n observability get all -l app=prometheus
kubectl port-forward svc/prometheus -n observability 9090:9090
```

### 5. Deploy Loki

```bash
kubectl -n observability apply -f loki.yaml
kubectl -n observability get all -l app=loki
curl -X GET "http://$(kubectl -n observability get svc -l app=loki -o json | jq -r '.items[].spec.clusterIP'):3100/ready"
```

### 6. Deploy Grafana

```bash
kubectl -n observability apply -f grafana.yaml
kubectl -n observability get all -l app=grafana
kubectl -n observability port-forward svc/grafana 3000:3000
```

### 7. Deploy OTEL Collector Gateway for Cluster Metrics

```bash
kubectl -n observability apply -f otel-collector-gateway-serviceaccount.yaml
kubectl -n observability apply -f otel-collector-gateway-configmap.yaml
kubectl -n observability apply -f otel-collector-gateway-deployment.yaml
kubectl -n observability apply -f otel-collector-gateway-service.yaml
kubectl -n observability get all -l app=otel-collector-gateway
```

---

## 📡 Access UIs

| Tool                   | URL                                              |
| ---------------------- | ------------------------------------------------ |
| **API**                | [http://localhost:8000](http://localhost:8000)   |
| **Grafana**            | [http://localhost:3000](http://localhost:3000)   |
| **Jaeger**             | [http://localhost:16686](http://localhost:16686) |
| **Prometheus**         | [http://localhost:9090](http://localhost:9090)   |
| **Loki (via Grafana)** | Integrated                                       |

---
## 📖 Learn More

This repository is based on the article series:  
**“The Observability Blueprint: Instrument, Deploy, Observe — OpenTelemetry in Action on Kubernetes”**  
[Read the full blog series here](https://github.com/Kartikdudeja/blogs/tree/main/otel-k8s-article-series)
