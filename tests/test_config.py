"""Tests for configuration management."""

import pytest
import tempfile
from pathlib import Path

from src.config import Config, load_config, validate_config


class TestConfigLoading:
    """Test configuration loading."""

    def test_load_default_config(self):
        """Test loading default config when file doesn't exist."""
        config = load_config("/nonexistent/path/config.yaml")
        assert isinstance(config, Config)
        assert not config.slack.enabled
        assert not config.discord.enabled
        assert not config.notion.enabled

    def test_load_config_from_file(self):
        """Test loading config from an actual file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
slack:
  enabled: true
  bot_token: "test-token"
  channels: ["general", "tech"]

indexing:
  lookback_days: 60
""")
            f.flush()

            config = load_config(f.name)
            assert config.slack.enabled
            assert config.slack.bot_token == "test-token"
            assert config.slack.channels == ["general", "tech"]
            assert config.indexing.lookback_days == 60

            # Cleanup
            Path(f.name).unlink()


class TestConfigValidation:
    """Test configuration validation."""

    def test_no_platforms_enabled(self):
        """Test warning when no platforms are enabled."""
        config = Config()
        warnings = validate_config(config)
        assert any("no platforms" in w.lower() for w in warnings)

    def test_slack_without_token(self):
        """Test warning when Slack is enabled but token is missing."""
        config = Config(
            slack={"enabled": True, "bot_token": "", "channels": ["general"]}
        )
        warnings = validate_config(config)
        assert any("slack" in w.lower() and "token" in w.lower() for w in warnings)

    def test_valid_configuration(self):
        """Test that valid configuration has no warnings."""
        config = Config(
            slack={
                "enabled": True,
                "bot_token": "test-token",
                "channels": ["general"],
            }
        )
        warnings = validate_config(config)
        # No warnings about missing tokens
        assert not any("token" in w.lower() for w in warnings)
