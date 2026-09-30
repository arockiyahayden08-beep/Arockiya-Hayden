from app.schemas import PromptRequest


def test_prompt_request_defaults():
    payload = PromptRequest(story_prompt="A fox finds a glowing tree.")
    assert payload.character_name == "Tara"
    assert payload.setting == "enchanted forest"


def test_prompt_request_strips_values():
    payload = PromptRequest(story_prompt="  A fox adventure  ", character_name="  Tara  ")
    assert payload.story_prompt == "A fox adventure"
    assert payload.character_name == "Tara"
