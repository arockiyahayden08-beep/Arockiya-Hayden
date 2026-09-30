from app.config import Settings
from app.schemas import PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout


def generate_comic(request: PromptRequest, settings: Settings) -> dict:
    outline = generate_outline(request, settings)
    story = generate_story(request, outline, settings)
    image_paths = [
        generate_image(
            request,
            panel.panel_number,
            panel.title,
            panel.scene_description,
            panel.image_prompt,
            settings,
        )
        for panel in outline.panels
    ]
    layout = build_comic_layout(outline, story, image_paths)
    pdf_path = save_pdf(layout, settings.exports_dir)
    return {"layout": layout, "pdf_path": pdf_path, "request": request.model_dump()}
