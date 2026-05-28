# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in a recipe or tool within this cookbook, please report it responsibly.

**Do not open a public issue.** Instead, email the maintainer directly.

We aim to acknowledge reports within 48 hours and provide an initial assessment within 5 business days.

## Scope

This policy applies to:

- Code samples that could lead to security vulnerabilities if used as-is in production
- Hardcoded credentials or secrets in recipes
- Insecure configurations in deployment examples

## Out of Scope

- Vulnerabilities in third-party dependencies referenced by recipes
- Security issues in the reader's own implementation

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| < 1.0   | :x:                |

Only the latest commit on `main` is supported. This project is pre-1.0 and evolving rapidly.
