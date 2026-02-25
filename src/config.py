"""Configuration management for team context collector."""

from pathlib import Path
from typing import Optional, List

import yaml
from pydantic import BaseModel, Field, field_validator


class SlackConfig(BaseModel):
    enabled: bool = False
    bot_token: str = ""
    channels: List[str] = Field(default_factory=list)

    @field_validator("channels", mode="before")
    @classmethod
    def parse_channels(cls, v):
        if isinstance(v, str):
            return [c.strip() for c in v.split(",")]
        return v or []


class DiscordConfig(BaseModel):
    enabled: bool = False
    bot_token: str = ""
    servers: List[dict] = Field(default_factory=list)


class NotionConfig(BaseModel):
    enabled: bool = False
    api_key: str = ""
    pages: List[str] = Field(default_factory=list)


class IndexingConfig(BaseModel):
    lookback_days: int = 30
    sync_interval: int = 60


class SearchConfig(BaseModel):
    top_k: int = 10
    similarity_threshold: float = 0.5


class Config(BaseModel):
    slack: SlackConfig = Field(default_factory=SlackConfig)
    discord: DiscordConfig = Field(default_factory=DiscordConfig)
    notion: NotionConfig = Field(default_factory=NotionConfig)
    indexing: IndexingConfig = Field(default_factory=IndexingConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)

    class Config:
        yaml_file = "config.yaml"


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from YAML file."""
    if config_path is None:
        config_path_obj = Path("config.yaml")
    else:
        config_path_obj = Path(config_path)

    if not config_path_obj.exists():
        # Return default config if file doesn't exist
        return Config()

    with open(config_path_obj, "r") as f:
        data = yaml.safe_load(f) or {}

    return Config(**data)


def validate_config(config: Config) -> List[str]:
    """Validate configuration and return any warnings."""
    warnings = []

    if not any([config.slack.enabled, config.discord.enabled, config.notion.enabled]):
        warnings.append("No platforms are enabled. Enable at least one (Slack, Discord, or Notion).")

    if config.slack.enabled and not config.slack.bot_token:
        warnings.append("Slack is enabled but bot_token is not set.")

    if config.discord.enabled and not config.discord.bot_token:
        warnings.append("Discord is enabled but bot_token is not set.")

    if config.notion.enabled and not config.notion.api_key:
        warnings.append("Notion is enabled but api_key is not set.")

    return warnings
