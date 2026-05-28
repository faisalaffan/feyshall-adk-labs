.PHONY: help dev test eval security lint format clean docker-up docker-down install

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Development ---

install: ## Install all dependencies
	pip install -r requirements.txt
	cd _languages/dart/adk_client && dart pub get
	cd _languages/dart/agent_chat && dart pub get

dev: ## Start local dev server (ADK web UI)
	adk web

serve: ## Start FastAPI agent server
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# --- Testing ---

test: ## Run all tests
	python -m pytest tests/ -v

eval: ## Run evaluation suite (requires GOOGLE_API_KEY)
	python -m pytest tests/eval/ -v

eval-safety: ## Run safety evaluation only
	python -m pytest tests/eval/test_safety.py -v

eval-accuracy: ## Run accuracy evaluation only
	python -m pytest tests/eval/test_accuracy.py -v

eval-security: ## Run prompt injection tests only
	python -m pytest tests/eval/test_prompt_injection.py -v

eval-regression: ## Run regression tests only
	python -m pytest tests/eval/test_regression.py -v

# --- Linting & Formatting ---

lint: ## Run all linters
	ruff check .
	mypy .
	cd _languages/dart/adk_client && dart analyze
	cd _languages/dart/agent_chat && dart analyze

format: ## Auto-format all code
	ruff format .
	cd _languages/dart/adk_client && dart format lib test
	cd _languages/dart/agent_chat && dart format lib test

# --- Security ---

security: ## Run security checks
	python -m pytest tests/eval/test_prompt_injection.py -v
	gitleaks detect --source . --config .gitleaks.toml

# --- Docker ---

docker-build: ## Build Docker image
	docker build -t adk-agent:latest .

docker-up: ## Start full stack (agent + Redis + LGTM)
	docker compose up -d

docker-down: ## Stop full stack
	docker compose down

docker-logs: ## Tail all service logs
	docker compose logs -f

# --- CI ---

ci-check: ## Run full CI check locally (lint + test + eval + security)
	make lint
	make test
	make eval
	make security

# --- Docs ---

docs-serve: ## Start MkDocs documentation server
	cd mkdocs && mkdocs serve

docs-build: ## Build static documentation site
	cd mkdocs && mkdocs build

# --- Cleanup ---

clean: ## Remove build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .dart_tool -exec rm -rf {} + 2>/dev/null || true
