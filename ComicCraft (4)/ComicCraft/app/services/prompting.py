from app.schemas import PromptRequest 
 
 
CARTOON_STYLE = ( 
    "polished high-quality 2D cartoon children's picture-book illustration, " 
    "cute expressive anthropomorphic fox, clean bold outlines, detailed soft fur, " 
    "large expressive eyes, rich saturated colors, cinematic lighting, magical forest atmosphere, " 
    "friendly wholesome visual storytelling, landscape 4:3 composition" 
) 
 
 
def character_bible(request: PromptRequest) -> str: 
    return ( 
        f"MAIN CHARACTER CONSISTENCY: {request.character_name} is the same cute anthropomorphic fox " 
        "in every panel. Keep the same face, orange-red fur, cream muzzle and chest, big expressive eyes, " 
        "small triangular ears, fluffy tail, child-friendly proportions, and the same outfit/accessories " 
        "unless the story explicitly requires a change. Do not redesign the character between panels." 
    ) 
 
 
def outline_prompt(request: PromptRequest, panel_count: int) -> str: 
    return f"""Create a coherent {panel_count}-panel comic outline. 
 
Story idea: {request.story_prompt} 
Hero: {request.character_name} 
Setting: {request.setting} 
Tone: {request.tone} 
Preferred visual style: {request.art_style} 
 
{character_bible(request)} 
 
Return ONLY valid JSON with this exact top-level shape: 
{{"panels":[{{"panel_number":1,"title":"...","scene_description":"...","image_prompt":"..."}}]}} 
 
Rules: 
- Exactly {panel_count} panels numbered 1 through {panel_count}. 
- Give every panel a clear beginning, middle, or ending role. 
- Keep the hero and setting visually consistent. 
- Image prompts must describe a single landscape 4:3 comic panel and must include the full cartoon style description. 
- Do not put speech bubbles or written words inside generated images. 
""" 
 
 
def story_prompt(request: PromptRequest, outline_json: str) -> str: 
    return f"""Write the narration and dialogue for this five-panel children's comic. 
 
Hero: {request.character_name} 
Setting: {request.setting} 
Tone: {request.tone} 
 
{character_bible(request)} 
 
Outline JSON: 
{outline_json} 
 
Return ONLY valid JSON: 
{{"panels":[{{"panel_number":1,"caption":"...","narration":"...","dialogue":["..."]}}]}} 
 
Rules: 
- Exactly five panels. 
- Dialogue must be short enough for a comic panel. 
- Keep continuity between panels. 
- Wholesome, clear, cinematic storytelling. 
""" 
 
 
def image_prompt(request: PromptRequest, panel_prompt: str, scene: str) -> str: 
    return f"""{CARTOON_STYLE}. 
{character_bible(request)} 
Scene: {scene} 
Visual direction: {panel_prompt} 
 
IMPORTANT: one clean comic illustration, no text, no letters, no logos, no watermark, no speech bubbles, no photorealism. """