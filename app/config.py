from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application settings
    app_name: str = "ComicCraft"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    debug: bool = True

    # Demo mode
    # True = application can run without external AI API keys.
    demo_mode: bool = False

    # Gemini settings
    gemini_api_key: str = ""
    gemini_outline_model: str = "gemini-2.5-flash"
    gemini_story_model: str = "gemini-2.5-flash"

    # Hugging Face settings
    hf_api_key: str = ""
    hf_image_model: str = "stabilityai/stable-diffusion-xl-base-1.0"

    # Image provider:
    # huggingface / local / auto
    image_provider: str = "huggingface"

    # Local Stable Diffusion model
    local_image_model: str = "runwayml/stable-diffusion-v1-5"

    # Image generation settings
    image_width: int = 768
    image_height: int = 768
    image_steps: int = 20
    image_guidance: float = 7.5

    # Comic settings
    panel_count: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()