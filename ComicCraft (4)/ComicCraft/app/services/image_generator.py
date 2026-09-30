from pathlib import Path

import torch
from diffusers import StableDiffusionPipeline

from app.config import Settings
from app.schemas import PromptRequest
from app.services.prompting import image_prompt


MODEL_ID = "stable-diffusion-v1-5/stable-diffusion-v1-5"

_PIPELINE = None


def _get_pipeline():
    global _PIPELINE

    if _PIPELINE is None:
        print("Loading local Stable Diffusion 1.5 model...")

        _PIPELINE = StableDiffusionPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float32,
        )

        _PIPELINE = _PIPELINE.to("cpu")

        print("Local Stable Diffusion model loaded.")

    return _PIPELINE


def generate_image(
    request: PromptRequest,
    panel_number: int,
    title: str,
    scene: str,
    visual_prompt: str,
    settings: Settings,
) -> str:

    path = settings.panels_dir / f"panel_{panel_number:02d}.png"
    path.parent.mkdir(parents=True, exist_ok=True)

    prompt = image_prompt(
        request,
        visual_prompt,
        scene,
    )

    prompt += """
IMPORTANT CHARACTER CONSISTENCY:
The main character is the same cute anthropomorphic orange fox
throughout the entire five-panel comic.

The fox must have:
- orange detailed fur
- white muzzle and chest
- large expressive eyes
- cute pointed ears
- small friendly black nose
- child-friendly proportions
- cute expressive face
- consistent body shape
- consistent character design from panel to panel

ART STYLE:
polished high-quality 2D cartoon children's picture-book illustration,
clean bold outlines,
detailed fur,
large expressive eyes,
rich saturated colors,
cinematic lighting,
magical forest atmosphere,
professional children's storybook artwork.

COMPOSITION:
one single comic illustration,
landscape 4:3 composition,
complete scene visible,
clear foreground and background,
no collage,
no multiple panels,
no text,
no letters,
no logos,
no watermark,
no speech bubbles,
no photorealism.

SCENE:
Follow the requested scene description closely.
"""

    print(
        f"Generating panel {panel_number}/{settings.panel_count} "
        "with local Stable Diffusion..."
    )

    try:
        pipe = _get_pipeline()

        result = pipe(
            prompt=prompt,
            width=512,
            height=384,
            num_inference_steps=20,
            guidance_scale=7.5,
        )

        image = result.images[0]

        # Resize to ComicCraft's configured output size.
        image = image.resize(
            (settings.image_width, settings.image_height)
        )

        image.save(path, "PNG")

        print(
            f"Panel {panel_number} generated successfully: {path}"
        )

        return str(path)

    except Exception as exc:
        print(
            f"Local Stable Diffusion generation failed "
            f"for panel {panel_number}: {exc}"
        )
        raise