---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Kubernetes Deployment

## Concept

Production agent deployments on Kubernetes with horizontal scaling, health checks, and graceful shutdown. Uses Helm for templating.

## Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adk-agent
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: adk-agent
  template:
    metadata:
      labels:
        app: adk-agent
    spec:
      containers:
        - name: agent
          image: adk-agent:latest
          ports:
            - containerPort: 8000
          env:
            - name: GOOGLE_API_KEY
              valueFrom:
                secretKeyRef:
                  name: adk-secrets
                  key: google-api-key
            - name: REDIS_URL
              value: "redis://redis-service:6379"
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 15
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
```

## Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: adk-agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: adk-agent
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Pods
      pods:
        metric:
          name: adk_active_sessions
        target:
          type: AverageValue
          averageValue: "50"
```

## Helm Chart Structure

```
helm/adk-agent/
├── Chart.yaml
├── values.yaml
├── values-prod.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   ├── configmap.yaml
│   └── secret.yaml
└── README.md
```

## Pitfalls

- **Session affinity**: If using `InMemorySessionService`, requests must go to the same pod. Use `sessionAffinity: ClientIP` on the Service. Better: use Redis session backend.
- **Graceful shutdown**: Agent pods may have in-flight LLM calls (5-30s). Set `terminationGracePeriodSeconds: 60` and handle SIGTERM.
- **HPA on LLM-dependent metrics**: If the LLM API is slow, CPU usage drops while latency spikes. HPA by CPU alone is insufficient. Add custom metrics.
