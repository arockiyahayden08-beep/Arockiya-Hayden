from app.config import Settings


def status(settings: Settings) -> dict:
    return {
        "app": "ok",
        "demo_mode": settings.demo_mode,
        "gemini_configured": bool(settings.gemini_api_key),
        "huggingface_configured": bool(settings.hf_token),
    }
