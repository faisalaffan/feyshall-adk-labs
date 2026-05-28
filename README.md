<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/01_LOGO.png">
    <img alt="feyshall-adk-labs banner" src="assets/01_LOGO.png" width="100%">
  </picture>
</p>

<p align="center">
  <a href="README.id.md">🇮🇩 Bahasa Indonesia</a>
</p>

<p align="center">
  <img alt="feyshall-adk-labs logo" src="assets/01_LOGO.png" width="120">
</p>

# feyshall-adk-labs

<p align="center">
  <a href="https://github.com/faisalaffan/feyshall-adk-labs/actions/workflows/eval.yml"><img alt="Eval CI" src="https://github.com/faisalaffan/feyshall-adk-labs/actions/workflows/eval.yml/badge.svg"></a>
  <a href="https://github.com/faisalaffan/feyshall-adk-labs/actions/workflows/security-scan.yml"><img alt="Security Scan" src="https://github.com/faisalaffan/feyshall-adk-labs/actions/workflows/security-scan.yml/badge.svg"></a>
  <a href="https://github.com/faisalaffan/feyshall-adk-labs/actions/workflows/dart.yml"><img alt="Dart CI" src="https://github.com/faisalaffan/feyshall-adk-labs/actions/workflows/dart.yml/badge.svg"></a>
  <a href="https://github.com/faisalaffan/feyshall-adk-labs/actions/workflows/go.yml"><img alt="Go CI" src="https://github.com/faisalaffan/feyshall-adk-labs/actions/workflows/go.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
  <a href="https://github.com/faisalaffan/feyshall-adk-labs"><img alt="GitHub stars" src="https://img.shields.io/github/stars/faisalaffan/feyshall-adk-labs"></a>
</p>

Google ADK Cookbook For Better Development Purpose

## Overview

A collection of practical recipes, patterns, and best practices for building with Google Agent Development Kit (ADK). This cookbook provides ready-to-use examples to accelerate your agent-based application development.

See the [Product Requirements Document](docs/PRD.md) for the full roadmap and chapter breakdown.

## Getting Started

```bash
# Clone the repository
git clone https://github.com/faisalaffan/feyshall-adk-labs.git
cd feyshall-adk-labs
```

## Structure

```
feyshall-adk-labs/
├── 00-foundations/          # ADK concepts, lifecycle, hello-world
├── 01-tools/                # Function tools, MCP, auth, error handling
├── 02-multi-agent/          # Orchestration patterns, routing, isolation
├── 03-memory-and-state/    # Sessions, Redis, vector memory
├── 04-streaming/            # SSE, audio, frontend integration
├── 05-evaluation-and-testing/ # Unit tests, eval metrics, CI pipelines
├── 06-observability/        # OTel, LGTM, metrics, alerting
├── 07-deployment/           # Docker, K8s, Vertex AI, Cloud Run
├── 08-enterprise-patterns/  # RBAC, audit, rate limiting, cost mgmt
├── 09-real-world-usecases/  # Inventory, support, code review, ERP
├── _languages/              # Python, Go, Java, Dart setup + SDK
├── .github/workflows/       # CI/CD pipelines
├── helm/                    # Kubernetes Helm chart
├── mkdocs/                  # Documentation site
├── assets/                  # Images and static assets
└── README.md                # You are here
```

## License

This project is licensed under the terms in [LICENSE](LICENSE).
