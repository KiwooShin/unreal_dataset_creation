"""
Pydantic settings for Unreal Dataset.

Configuration is loaded from (in order of precedence):
1. Environment variables (UNREAL_* prefix)
2. .env file in current directory
3. Default values defined here
"""

from functools import lru_cache
from pathlib import Path
from typing import Tuple

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    """Settings for the Unreal HTTP API server."""

    model_config = SettingsConfigDict(
        env_prefix="UNREAL_SERVER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = Field(default="localhost", description="Server host")
    port: int = Field(default=8080, description="Server port")


class CaptureSettings(BaseSettings):
    """Settings for screenshot capture."""

    model_config = SettingsConfigDict(
        env_prefix="UNREAL_CAPTURE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    fov: float = Field(default=90.0, description="Camera field of view in degrees")
    resolution_width: int = Field(default=640, description="Image width in pixels")
    resolution_height: int = Field(default=640, description="Image height in pixels")
    screenshot_timeout: int = Field(default=60, description="Timeout for screenshot capture in seconds")
    stabilization_delay: float = Field(default=1.0, description="Delay before capture for viewport stabilization")

    @property
    def resolution(self) -> Tuple[int, int]:
        """Get resolution as tuple."""
        return (self.resolution_width, self.resolution_height)


class Settings(BaseSettings):
    """Main settings for Unreal Dataset."""

    model_config = SettingsConfigDict(
        env_prefix="UNREAL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Paths
    output_dir: Path = Field(
        default=Path("./dataset_output"),
        description="Output directory for images and labels"
    )
    assets_dir: Path = Field(
        default=Path("./assets"),
        description="Directory containing scene configuration files"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Path | None = Field(default=None, description="Optional log file path")

    # Nested settings
    server: ServerSettings = Field(default_factory=ServerSettings)
    capture: CaptureSettings = Field(default_factory=CaptureSettings)

    @property
    def api_url(self) -> str:
        """Get the full API URL."""
        return f"http://{self.server.host}:{self.server.port}"

    def ensure_directories(self) -> None:
        """Create output directories if they don't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "labels").mkdir(exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
