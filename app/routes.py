
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.schemas import PromptRequest
from app.services.comic_pipeline import generate_comic
from app.services.image_generator import generate_image


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()


# ---------------------------------------------------------
# Home Page
# ---------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Display the ComicCraft homepage.

    The homepage allows users to enter:
    - Story prompt
    - Character name
    - Setting
    - Story tone
    - Art style
    """

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "ComicCraft - AI Comic Story Creator"
        },
    )


# ---------------------------------------------------------
# Generate Comic - HTML Form
# ---------------------------------------------------------

@router.post("/generate", response_class=HTMLResponse)
async def generate_comic_form(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    """
    Generate a complete comic from the HTML form.

    Workflow:

    1. Generate 5-panel outline
    2. Generate narration/dialogue
    3. Generate images
    4. Build comic layout
    5. Generate PDF
    6. Display comic preview
    """

    try:
        result = await generate_comic(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "title": "ComicCraft - Comic Preview",
                "layout": result["layout"],
                "pdf_url": result["pdf_url"],
                "request_data": {
                    "story_prompt": story_prompt,
                    "character_name": character_name,
                    "setting": setting,
                    "tone": tone,
                    "art_style": art_style,
                },
            },
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Comic generation failed: {exc}",
        ) from exc


# ---------------------------------------------------------
# Generate Comic - JSON API
# ---------------------------------------------------------

@router.post("/generate-comic/json")
async def generate_comic_json(payload: PromptRequest):
    """
    Generate a comic using a JSON request.

    This endpoint is intended for:
    - API clients
    - Postman
    - Swagger UI
    - JavaScript applications
    """

    try:
        result = await generate_comic(
            story_prompt=payload.story_prompt,
            character_name=payload.character_name,
            setting=payload.setting,
            tone=payload.tone,
            art_style=payload.art_style,
        )

        return {
            "success": True,
            "message": "Comic generated successfully.",
            "layout": result["layout"],
            "pdf_url": result["pdf_url"],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Comic generation failed: {exc}",
        ) from exc


# ---------------------------------------------------------
# Test Image Generation
# ---------------------------------------------------------

@router.post("/test-image")
async def test_image(prompt: str = Form(...)):
    """
    Developer utility endpoint for testing image generation
    without generating an entire comic.
    """

    if not prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="Image prompt cannot be empty.",
        )

    try:
        image_path = await generate_image(prompt)

        return {
            "success": True,
            "message": "Image generated successfully.",
            "image_url": image_path,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Image generation failed: {exc}",
        ) from exc


# ---------------------------------------------------------
# Export Success Page
# ---------------------------------------------------------

@router.get("/export-success", response_class=HTMLResponse)
async def export_success(
    request: Request,
    pdf_url: str | None = None,
):
    """
    Display the PDF export success page.
    """

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "title": "ComicCraft - Export Successful",
            "pdf_url": pdf_url,
        },
    )


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@router.get("/health")
async def health_check():
    """
    Simple application health-check endpoint.
    """

    return {
        "status": "healthy",
        "service": "ComicCraft",
    }

