"""Tests for DebtConfig."""

from techdebt.core.config import DebtConfig


def test_config_defaults() -> None:
    config = DebtConfig()
    assert config.industry == "fintech"
    assert config.complexity_threshold == 10
    assert config.dependency_age_days == 365
    assert config.max_files == 200


def test_config_custom() -> None:
    config = DebtConfig(industry="manufacturing", complexity_threshold=15)
    assert config.industry == "manufacturing"
    assert config.complexity_threshold == 15