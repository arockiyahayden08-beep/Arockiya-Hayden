from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    gemini_api_key: str | None = None
    gemini_image_api_key: str | None = None
    hf_token: str | None = None
    gemini_flash_model: str = "gemini-3.5-flash-lite"
    gemini_pro_model: str = "gemini-3.5-flash"
    gemini_image_model: str = "gemini-3.1-flash-image"
    hf_image_model: str = "black-forest-labs/FLUX.1-schnell"
    hf_image_fallback_model: str = "stabilityai/stable-diffusion-3.5-large-turbo"
    panel_count: int = 5
    image_width: int = 1024
    image_height: int = 768
    demo_mode: bool = False

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def templates_dir(self) -> Path:
        return BASE_DIR / "templates"

    @property
    def static_dir(self) -> Path:
        return BASE_DIR / "static"

    @property
    def panels_dir(self) -> Path:
        return self.static_dir / "panels"

    @property
    def exports_dir(self) -> Path:
        return self.static_dir / "exports"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.panels_dir.mkdir(parents=True, exist_ok=True)
    settings.exports_dir.mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()