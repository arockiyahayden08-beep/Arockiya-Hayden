import json
import time
from typing import Any

from app.config import Settings
from app.schemas import ComicOutline, PanelOutline, PromptRequest
from app.services.prompting import outline_prompt


def _extract_json(text: str) -> Any:
    text = text.strip().replace("```json", "").replace("```", "").strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("Gemini did not return JSON.")

    return json.loads(text[start:end + 1])


def _demo_outline(request: PromptRequest, count: int) -> ComicOutline:
    beats = [
        (
            "A Curious Beginning",
            f"{request.character_name} notices something unusual in the {request.setting}."
        ),
        (
            "Into the Adventure",
            f"{request.character_name} follows the mystery deeper into the {request.setting}."
        ),
        (
            "A Surprising Problem",
            f"A playful obstacle appears and {request.character_name} must think creatively."
        ),
        (
            "The Brave Idea",
            f"{request.character_name} finds a clever, kind solution with a little help from the surroundings."
        ),
        (
            "A Happy Ending",
            f"{request.character_name} celebrates the discovery and returns home with a new story to tell."
        ),
    ]

    panels = []

    for i in range(count):
        title, scene = beats[i % len(beats)]

        panels.append(
            PanelOutline(
                panel_number=i + 1,
                title=title,
                scene_description=scene,
                image_prompt=(
                    f"{scene}; cheerful magical cartoon adventure scene"
                ),
            )
        )

    return ComicOutline(panels=panels)


def generate_outline(
    request: PromptRequest,
    settings: Settings,
) -> ComicOutline:

    # ---------------------------------------------------------
    # Demo mode / missing API key
    # ---------------------------------------------------------
    if not settings.gemini_api_key or settings.demo_mode:
        return _demo_outline(
            request,
            settings.panel_count,
        )

    # ---------------------------------------------------------
    # Gemini client
    # ---------------------------------------------------------
    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    # ---------------------------------------------------------
    # Retry configuration
    # ---------------------------------------------------------
    max_attempts = 3

    for attempt in range(1, max_attempts + 1):

        try:
            print(
                f"Generating comic outline with Gemini "
                f"{settings.gemini_flash_model} "
                f"(attempt {attempt}/{max_attempts})..."
            )

            # -------------------------------------------------
            # Gemini story / outline generation
            # -------------------------------------------------
            response = client.models.generate_content(
                model=settings.gemini_flash_model,
                contents=outline_prompt(
                    request,
                    settings.panel_count,
                ),
                config=types.GenerateContentConfig(
                    temperature=0.9,
                    max_output_tokens=3000,
                    response_mime_type="application/json",
                ),
            )

            # -------------------------------------------------
            # Extract JSON
            # -------------------------------------------------
            data = _extract_json(
                response.text or ""
            )

            # -------------------------------------------------
            # Validate ComicOutline
            # -------------------------------------------------
            outline = ComicOutline.model_validate(
                data
            )

            # -------------------------------------------------
            # Make sure we received exactly 5 panels
            # -------------------------------------------------
            if len(outline.panels) != settings.panel_count:
                raise ValueError(
                    f"Expected {settings.panel_count} panels, "
                    f"got {len(outline.panels)}."
                )

            print(
                "Comic outline generated successfully."
            )

            return outline

        # -----------------------------------------------------
        # Gemini/API error
        # -----------------------------------------------------
        except Exception as exc:

            error_text = str(exc)

            print(
                f"Gemini outline generation failed "
                f"on attempt {attempt}:"
            )

            print(error_text)

            # -------------------------------------------------
            # Retry if attempts remain
            # -------------------------------------------------
            if attempt < max_attempts:

                delay = 5 * (2 ** (attempt - 1))

                print(
                    f"Waiting {delay} seconds before "
                    f"retrying the comic outline..."
                )

                time.sleep(delay)

            # -------------------------------------------------
            # Final failure
            # -------------------------------------------------
            else:

                print(
                    "All Gemini outline attempts failed."
                )

                # Re-raise the original error so the
                # ComicCraft error page still receives it.
                raise