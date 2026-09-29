from pathlib import Path
from uuid import uuid4

import httpx
from PIL import Image, ImageDraw, ImageFont

from app.config import settings


PANELS_DIR = Path("static/panels")
PANELS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def generate_image(
    prompt: str,
    panel_number: int,
) -> str:
    """
    Generate an image for a comic panel.

    Returns the browser-accessible static path.
    """

    if not prompt.strip():
        raise ValueError(
            "Image prompt cannot be empty."
        )

    filename = (
        f"panel_{panel_number}_"
        f"{uuid4().hex[:8]}.png"
    )

    output = PANELS_DIR / filename

    if settings.demo_mode:
        _create_demo_image(
            prompt,
            panel_number,
            output,
        )

    else:
        provider = settings.image_provider.lower()

        if provider == "huggingface":
            _generate_huggingface(
                prompt,
                output,
            )

        elif provider == "local":
            _generate_local(
                prompt,
                output,
            )

        elif provider == "auto":
            try:
                _generate_local(
                    prompt,
                    output,
                )
            except Exception:
                _generate_huggingface(
                    prompt,
                    output,
                )

        else:
            raise ValueError(
                "IMAGE_PROVIDER must be "
                "'huggingface', 'local', or 'auto'."
            )

    return f"/static/panels/{filename}"


def _generate_huggingface(
    prompt: str,
    output: Path,
) -> None:
    """
    Generate an image using Hugging Face inference.
    """

    if not settings.hf_api_key:
        raise RuntimeError(
            "HF_API_KEY is not configured. "
            "Add it to .env or enable DEMO_MODE=true."
        )

    url = (
        "https://router.huggingface.co/"
        f"hf-inference/models/{settings.hf_image_model}"
    )

    headers = {
        "Authorization": (
            f"Bearer {settings.hf_api_key}"
        ),
        "Accept": "image/png",
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "width": settings.image_width,
            "height": settings.image_height,
        },
    }

    with httpx.Client(timeout=180.0) as client:
        response = client.post(
            url,
            headers=headers,
            json=payload,
        )

        response.raise_for_status()

    content_type = response.headers.get(
        "content-type",
        "",
    )

    if "image" not in content_type:
        raise RuntimeError(
            "Hugging Face did not return an image."
        )

    output.write_bytes(
        response.content
    )


def _generate_local(
    prompt: str,
    output: Path,
) -> None:
    """
    Generate an image locally using Diffusers.

    This requires a suitable Python environment and
    sufficient CPU/GPU resources.
    """

    try:
        import torch
        from diffusers import StableDiffusionPipeline
    except ImportError as exc:
        raise RuntimeError(
            "Local image generation requires "
            "torch and diffusers."
        ) from exc

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    dtype = (
        torch.float16
        if device == "cuda"
        else torch.float32
    )

    pipe = StableDiffusionPipeline.from_pretrained(
        settings.local_image_model,
        torch_dtype=dtype,
    )

    pipe = pipe.to(device)

    result = pipe(
        prompt,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps,
        guidance_scale=settings.image_guidance,
    )

    result.images[0].save(
        output,
        format="PNG",
    )


def _create_demo_image(
    prompt: str,
    panel_number: int,
    output: Path,
) -> None:
    """
    Create a simple placeholder image for DEMO_MODE.

    This allows the complete application to be tested
    without an image-generation API.
    """

    width = 900
    height = 600

    image = Image.new(
        "RGB",
        (width, height),
        "white",
    )

    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (20, 20, width - 20, height - 20),
        outline="black",
        width=6,
    )

    draw.rectangle(
        (80, 80, 820, 380),
        outline="black",
        width=4,
    )

    draw.ellipse(
        (310, 140, 590, 420),
        outline="black",
        width=5,
    )

    draw.rectangle(
        (520, 420, 790, 520),
        outline="black",
        width=4,
    )

    try:
        font = ImageFont.truetype(
            "arial.ttf",
            28,
        )
    except OSError:
        font = ImageFont.load_default()

    draw.text(
        (45, 40),
        f"ComicCraft - Panel {panel_number}",
        fill="black",
        font=font,
    )

    prompt_text = prompt[:150].replace(
        "\n",
        " ",
    )

    draw.text(
        (100, 450),
        "DEMO IMAGE",
        fill="black",
        font=font,
    )

    draw.text(
        (100, 500),
        prompt_text,
        fill="black",
        font=font,
    )

    image.save(
        output,
        format="PNG",
    )