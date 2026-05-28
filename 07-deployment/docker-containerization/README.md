---
adk_version: "1.28"
level: intermediate
languages: [python, go]
---

# Docker Containerization

## Concept

Package your ADK agent as a Docker container for consistent deployment. Multi-stage builds keep images small and secure.

## Python Dockerfile

```dockerfile
# Stage 1: Build
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .

EXPOSE 8000
USER 1000:1000  # Non-root
HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Go Dockerfile

```dockerfile
# Stage 1: Build
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o agent .

# Stage 2: Runtime (scratch = minimal)
FROM scratch
COPY --from=builder /app/agent /agent
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

EXPOSE 8000
USER 1000:1000
ENTRYPOINT ["/agent"]
```

## Docker Compose (Agent + Dependencies)

```yaml
version: "3.8"
services:
  agent:
    build: .
    ports: ["8000:8000"]
    environment:
      GOOGLE_API_KEY: ${GOOGLE_API_KEY}
      REDIS_URL: redis://redis:6379
    depends_on:
      redis:
        condition: service_healthy

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
```

## Image Size Comparison

| Language | Base Image | Final Size |
|----------|-----------|------------|
| Python | python:3.12-slim | ~200MB |
| Python (multi-stage) | python:3.12-slim | ~150MB |
| Go | scratch | ~15MB |
| Java | eclipse-temurin:17-jre | ~250MB |

## Pitfalls

- **API keys in image layers**: `ENV GOOGLE_API_KEY=xxx` in Dockerfile commits the key to image history. Always pass at runtime via `--env-file` or secrets manager.
- **Python image bloat**: `pip install` without `--no-cache-dir` adds 100MB+ of pip cache. Always use it in Dockerfiles.
- **Non-root user**: Running as root means a compromised agent owns the container. Always `USER 1000`.
