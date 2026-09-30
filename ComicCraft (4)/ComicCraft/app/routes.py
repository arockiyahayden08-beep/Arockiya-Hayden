from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.schemas import PromptRequest
from app.services.image_generator import generate_image
from app.services.workflow import generate_comic


router = APIRouter()

settings = get_settings()

templates = Jinja2Templates(
    directory=str(settings.templates_dir)
)


def _render(request: Request, template: str, context: dict):
    return templates.TemplateResponse(
        request=request,
        name=template,
        context=context,
    )


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return _render(
        request,
        "index.html",
        {
            "demo_mode": settings.demo_mode
        },
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate_form(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form("Tara"),
    setting: str = Form("enchanted forest"),
    tone: str = Form("funny"),
    art_style: str = Form("cartoon picture-book"),
):
    try:
        payload = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        result = generate_comic(payload, settings)

        # Convert the local Windows PDF path into a public
        # ComicCraft download URL.
        if result.get("pdf_path"):
            result["pdf_path"] = (
                "/export/" + Path(result["pdf_path"]).name
            )

        return _render(
            request,
            "comic_preview.html",
            result,
        )

    except Exception as exc:
        return _render(
            request,
            "error.html",
            {
                "error": str(exc)
            },
        )


@router.post("/generate-comic/json")
async def generate_json(payload: PromptRequest):
    try:
        result = generate_comic(payload, settings)

        public_pdf = (
            "/export/" + Path(result["pdf_path"]).name
        )

        public_layout = []

        for panel in result["layout"]:
            item = dict(panel)

            item["image_path"] = (
                "/panels/" + item["image_filename"]
            )

            public_layout.append(item)

        return {
            "success": True,
            "layout": public_layout,
            "pdf_path": public_pdf,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.post("/test-image", response_class=HTMLResponse)
async def test_image(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form("Tara"),
):
    try:
        payload = PromptRequest(
            story_prompt=prompt,
            character_name=character_name,
        )

        image_path = generate_image(
            payload,
            1,
            "Image Test",
            prompt,
            prompt,
            settings,
        )

        return _render(
            request,
            "image_test.html",
            {
                "image_url": "/panels/" + Path(image_path).name,
                "prompt": prompt,
            },
        )

    except Exception as exc:
        return _render(
            request,
            "error.html",
            {
                "error": str(exc)
            },
        )


@router.get("/export/{filename}")
async def download_export(filename: str):
    # Only use the filename portion, never a full filesystem path.
    safe_name = Path(filename).name

    file_path = settings.exports_dir / safe_name

    if (
        not file_path.exists()
        or file_path.suffix.lower() != ".pdf"
    ):
        raise HTTPException(
            status_code=404,
            detail="PDF not found",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=safe_name,
    )


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(
    request: Request,
    filename: str = "",
):
    return _render(
        request,
        "export_success.html",
        {
            "filename": Path(filename).name if filename else ""
        },
    )