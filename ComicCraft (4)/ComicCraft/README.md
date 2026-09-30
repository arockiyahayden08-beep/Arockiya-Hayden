# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI + Jinja2 web application that turns a short idea into a five-panel comic. It follows the supplied project specification while using current AI client libraries.

## Features

- Five-panel structured outline generation with Gemini Flash.
- Detailed narration/dialogue generation with Gemini Pro.
- Cartoon-style image generation through Hugging Face Inference Providers.
- Strong character-consistency prompt: the same hero description is repeated across all five panels.
- Demo mode with locally generated cartoon placeholders when API keys are unavailable.
- Responsive web UI.
- JSON API at `/generate-comic/json`.
- Image test endpoint at `/test-image`.
- PDF export with one panel per page.
- Automatic cleanup of invalid AI responses and safe filenames.

## Architecture

```text
Browser/Jinja2
      |
      v
FastAPI routes.py
      |
      +--> Gemini Flash ----> 5-panel outline
      |
      +--> Gemini Pro ------> narration/dialogue
      |
      +--> Hugging Face ----> cartoon panel images
      |
      +--> layout_builder --> panel layout
      |
      +--> exporters ------> PDF
```

## Requirements

- Windows 10/11, macOS, or Linux
- Python 3.11 or newer
- A Gemini API key for live story generation
- A Hugging Face token with Inference Providers access for live images
- Internet access for live AI generation

The project can still be opened and tested without keys because `DEMO_MODE=true` produces deterministic cartoon-style placeholder artwork.

## Windows / VS Code setup

```powershell
cd ComicCraft
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and set:

```env
GEMINI_API_KEY=your_gemini_key
HF_TOKEN=your_huggingface_token
DEMO_MODE=false
```

Then run:

```powershell
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 and API docs at http://127.0.0.1:8000/docs.

## If PowerShell blocks activation

Use:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Test

With the virtual environment active:

```powershell
pytest -q
```

The tests do not call external AI services.

## API example

POST `/generate-comic/json`:

```json
{
  "story_prompt": "A brave fox discovers a glowing tree in an enchanted forest.",
  "character_name": "Tara",
  "setting": "enchanted forest",
  "tone": "funny",
  "art_style": "cartoon picture-book"
}
```

## Image model note

The supplied document names Stable Diffusion and Hugging Face Diffusers. This implementation avoids forcing every Windows machine to download a multi-gigabyte local diffusion checkpoint. It uses Hugging Face's hosted Inference Providers through `huggingface_hub.InferenceClient`, with the model configurable in `.env`. A Stable Diffusion 3.5 model is provided as an optional fallback. This is substantially easier to install and run reliably on ordinary development machines.

## Troubleshooting

### `GEMINI_API_KEY is missing`
Set the key in `.env`, or leave `DEMO_MODE=true` to test the application without live Gemini calls.

### Hugging Face image generation fails
Check `HF_TOKEN`, model availability, provider credits/access, and `HF_IMAGE_MODEL`. The app will try the configured fallback model and then create a local cartoon placeholder so a single image-provider failure does not crash the complete comic workflow.

### Want local Diffusers instead?
The application keeps image generation behind `app/services/image_generator.py`. A local Diffusers implementation can be substituted there without changing routes, templates, layout, or PDF export.
