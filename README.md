# TechDebtLedger

> Automated tech debt tracker — scans repos for complexity hotspots and surfaces a prioritized payoff roadmap.

![CI](https://github.com/brianpelow/TechDebtLedger/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)

## Overview

`TechDebtLedger` scans your codebase and produces a prioritized, data-driven
tech debt payoff roadmap. It identifies complexity hotspots, annotated debt
items (TODO/FIXME/HACK), outdated dependencies, and duplication density —
then ranks them by estimated remediation value.

Built for engineering leaders in regulated financial services and manufacturing
where unmanaged tech debt creates audit risk, slows delivery, and increases
the blast radius of incidents.

## API endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Service health check |
| `POST /scan` | Scan a repository and return debt inventory |
| `GET /scan/{scan_id}/summary` | Get debt summary for a completed scan |
| `GET /scan/{scan_id}/roadmap` | Get prioritized payoff roadmap |
| `GET /scan/{scan_id}/hotspots` | Get top complexity hotspots |
| `GET /scan/{scan_id}/todos` | Get all annotated debt items |
| `GET /scan/{scan_id}/narrative` | AI-generated debt narrative |

## Debt categories scanned

| Category | Signal | Priority weight |
|----------|--------|-----------------|
| Complexity hotspots | Cyclomatic complexity > threshold | High |
| Annotated debt | TODO/FIXME/HACK/XXX comments | Medium |
| Dependency age | Packages > 12 months since release | Medium |
| Duplication | Repeated code blocks > 10 lines | Low |

## Quick start

```bash
pip install TechDebtLedger

tech-debt-ledger
# API at http://localhost:8000

# Scan a repo
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d "{\"repo_path\": \"./my-service\", \"name\": \"my-service\"}"
```

## Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | For AI debt narratives | No |
| `DEBT_INDUSTRY` | Industry context | No |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).