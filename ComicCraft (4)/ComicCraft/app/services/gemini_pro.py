import json
import time
from typing import Any

from app.config import Settings
from app.schemas import (
    ComicOutline,
    ComicStory,
    PanelStory,
    PromptRequest,
)
from app.services.prompting import story_prompt


def _extract_json(text: str) -> Any:
    text = text.strip()

    # Remove Markdown code fences if Gemini added them.
    text = text.replace("```json", "").replace("```", "").strip()

    start = text.find("{")

    if start == -1:
        raise ValueError("Gemini did not return story JSON.")

    decoder = json.JSONDecoder()

    try:
        data, _ = decoder.raw_decode(text[start:])
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Gemini returned invalid story JSON: {exc}"
        ) from exc

    return data


def _normalize_story_data(data: Any) -> dict:
    """
    Make Gemini's response match the ComicStory schema.

    Expected:
        {"panels": [...]}

    If Gemini returns one panel:
        {"panel_number": 1, ...}

    convert it to:
        {"panels": [{"panel_number": 1, ...}]}
    """

    if isinstance(data, dict) and "panels" in data:
        return data

    if isinstance(data, dict) and "panel_number" in data:
        return {
            "panels": [data]
        }

    if isinstance(data, list):
        return {
            "panels": data
        }

    raise ValueError(
        "Gemini returned an unexpected story format."
    )


def _demo_story(
    outline: ComicOutline,
    request: PromptRequest,
) -> ComicStory:

    panels = []

    for panel in outline.panels:
        panels.append(
            PanelStory(
                panel_number=panel.panel_number,
                caption=f"The {request.setting} hums with mystery...",
                narration=panel.scene_description,
                dialogue=[
                    f"{request.character_name}: "
                    "This adventure is getting interesting!"
                ],
            )
        )

    return ComicStory(panels=panels)


def generate_story(
    request: PromptRequest,
    outline: ComicOutline,
    settings: Settings,
) -> ComicStory:

    # ---------------------------------------------------------
    # Demo mode / missing API key
    # ---------------------------------------------------------
    if not settings.gemini_api_key or settings.demo_mode:
        return _demo_story(
            outline,
            request,
        )

    # ---------------------------------------------------------
    # Gemini client
    # ---------------------------------------------------------
    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    outline_json = outline.model_dump_json()

    # ---------------------------------------------------------
    # Retry configuration
    # ---------------------------------------------------------
    max_attempts = 3

    for attempt in range(1, max_attempts + 1):

        try:
            print(
                f"Generating detailed comic story with Gemini "
                f"{settings.gemini_pro_model} "
                f"(attempt {attempt}/{max_attempts})..."
            )

            # -------------------------------------------------
            # Gemini story generation
            # -------------------------------------------------
            response = client.models.generate_content(
                model=settings.gemini_pro_model,
                contents=story_prompt(
                    request,
                    outline_json,
                ),
                config=types.GenerateContentConfig(
                    temperature=0.95,
                    max_output_tokens=4000,
                    response_mime_type="application/json",
                ),
            )

            # -------------------------------------------------
            # Extract JSON
            # -------------------------------------------------
            story_data = _extract_json(
                response.text or ""
            )

            # -------------------------------------------------
            # Normalize Gemini response
            # -------------------------------------------------
            normalized_data = _normalize_story_data(
                story_data
            )

            # -------------------------------------------------
            # Validate against ComicStory schema
            # -------------------------------------------------
            story = ComicStory.model_validate(
                normalized_data
            )

            # -------------------------------------------------
            # Make sure all five panels are present
            # -------------------------------------------------
            if len(story.panels) != len(outline.panels):
                raise ValueError(
                    "Story response did not contain "
                    f"{len(outline.panels)} panels."
                )

            print(
                "Detailed comic story generated successfully."
            )

            return story

        # -----------------------------------------------------
        # Gemini/API/validation error
        # -----------------------------------------------------
        except Exception as exc:

            error_text = str(exc)

            print(
                f"Gemini story generation failed "
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
                    f"retrying the detailed story..."
                )

                time.sleep(delay)

            # -------------------------------------------------
            # Final failure
            # -------------------------------------------------
            else:

                print(
                    "All Gemini story-generation attempts failed."
                )

                raise