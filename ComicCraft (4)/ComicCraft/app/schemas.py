from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    story_prompt: str = Field(min_length=5, max_length=2000)
    character_name: str = Field(default="Tara", min_length=1, max_length=80)
    setting: str = Field(default="enchanted forest", min_length=1, max_length=200)
    tone: str = Field(default="funny", min_length=1, max_length=80)
    art_style: str = Field(default="cartoon picture-book", min_length=1, max_length=120)

    @field_validator("story_prompt", "character_name", "setting", "tone", "art_style")
    @classmethod
    def strip_values(cls, value: str) -> str:
        return value.strip()


class PanelOutline(BaseModel):
    panel_number: int = Field(ge=1)
    title: str
    scene_description: str
    image_prompt: str


class ComicOutline(BaseModel):
    panels: list[PanelOutline]


class PanelStory(BaseModel):
    panel_number: int = Field(ge=1)
    caption: str = ""
    narration: str = ""
    dialogue: list[str] = []


class ComicStory(BaseModel):
    panels: list[PanelStory]
