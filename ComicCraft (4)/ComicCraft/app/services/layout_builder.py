from pathlib import Path

from app.schemas import ComicOutline, ComicStory


def build_comic_layout(outline: ComicOutline, story: ComicStory, image_paths: list[str]) -> list[dict]:
    story_by_panel = {item.panel_number: item for item in story.panels}
    layout = []
    for index, panel in enumerate(outline.panels):
        item = story_by_panel.get(panel.panel_number)
        layout.append({
            "panel_number": panel.panel_number,
            "title": panel.title,
            "scene_description": panel.scene_description,
            "image_prompt": panel.image_prompt,
            "image_path": image_paths[index],
            "image_filename": Path(image_paths[index]).name,
            "caption": item.caption if item else "",
            "narration": item.narration if item else "",
            "dialogue": item.dialogue if item else [],
        })
    return layout
