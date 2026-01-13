#!/bin/bash
echo "🚀 Initiating Production Deployment of KoshaTrack..."

# 1. Build and Push Image
docker build -t koshatrack/ssa-engine:v0.1.0 .
# docker push koshatrack/ssa-engine:v0.1.0

# 2. Apply Kubernetes Manifests
kubectl apply -f k8s/production.yaml

# 3. Verify Health
echo "⏳ Waiting for pods to stabilize..."
kubectl get pods -w
