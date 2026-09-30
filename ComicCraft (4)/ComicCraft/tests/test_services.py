from pathlib import Path
from app.config import Settings
from app.schemas import PromptRequest
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout
from app.services.exporters import save_pdf


def test_demo_workflow(tmp_path):
    settings = Settings(demo_mode=True, panel_count=5, panels_dir=tmp_path / "panels", exports_dir=tmp_path / "exports")
    request = PromptRequest(story_prompt="A brave fox explores a magical forest.")
    outline = generate_outline(request, settings)
    story = generate_story(request, outline, settings)
    paths = [generate_image(request, p.panel_number, p.title, p.scene_description, p.image_prompt, settings) for p in outline.panels]
    assert len(outline.panels) == 5
    assert len(story.panels) == 5
    assert all(Path(p).exists() for p in paths)
    layout = build_comic_layout(outline, story, paths)
    pdf = save_pdf(layout, settings.exports_dir)
    assert Path(pdf).exists()
    assert Path(pdf).stat().st_size > 1000
