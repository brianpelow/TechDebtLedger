# Contributing

## Development setup

```bash
git clone https://github.com/brianpelow/TechDebtLedger
cd TechDebtLedger
uv sync
uv run pytest
uv run tech-debt-ledger
```

## Standards

- All PRs require passing CI
- Test coverage must not decrease
- Update CHANGELOG.md for user-facing changes