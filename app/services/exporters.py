from datetime import datetime
from pathlib import Path
from uuid import uuid4

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


EXPORT_DIR = Path("static/exports")

EXPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def _get_image_path(
    image_path: str,
) -> Path:
    """
    Convert a browser static path into
    a local filesystem path.
    """

    if image_path.startswith("/static/"):
        return Path(image_path.lstrip("/"))

    return Path(image_path)


def _draw_paragraph(
    pdf: canvas.Canvas,
    label: str,
    text: str,
    x: float,
    y: float,
    page_width: float,
    font_size: int = 9,
) -> float:
    """
    Draw wrapped text and return the new y position.
    """

    pdf.setFont(
        "Helvetica-Bold",
        font_size,
    )

    pdf.drawString(
        x,
        y,
        label,
    )

    y -= 14

    pdf.setFont(
        "Helvetica",
        font_size,
    )

    text = text or ""

    words = text.split()
    line = ""

    max_width = page_width - 80

    for word in words:
        candidate = (
            f"{line} {word}".strip()
        )

        if pdf.stringWidth(
            candidate,
            "Helvetica",
            font_size,
        ) > max_width:

            if line:
                pdf.drawString(
                    x,
                    y,
                    line,
                )

                y -= 12

            line = word

        else:
            line = candidate

    if line:
        pdf.drawString(
            x,
            y,
            line,
        )

        y -= 18

    return y


def save_pdf(
    title: str,
    layout: list[dict],
) -> str:
    """
    Compile the comic into a multi-page PDF.

    Each panel receives its own page.
    """

    filename = (
        f"comic_"
        f"{datetime.now():%Y%m%d_%H%M%S}_"
        f"{uuid4().hex[:6]}.pdf"
    )

    output = EXPORT_DIR / filename

    page_width, page_height = A4

    pdf = canvas.Canvas(
        str(output),
        pagesize=A4,
    )

    pdf.setTitle(title)

    for index, panel in enumerate(
        layout,
        start=1,
    ):
        # Page title
        pdf.setFont(
            "Helvetica-Bold",
            18,
        )

        pdf.drawString(
            40,
            page_height - 45,
            f"Panel {index}: "
            f"{panel.get('title', '')}",
        )

        # Image
        image_path = _get_image_path(
            panel.get(
                "image_path",
                "",
            )
        )

        image_top = page_height - 75
        image_width = page_width - 80
        image_height = 330

        if image_path.exists():
            try:
                pdf.drawImage(
                    ImageReader(
                        str(image_path)
                    ),
                    40,
                    image_top - image_height,
                    width=image_width,
                    height=image_height,
                    preserveAspectRatio=True,
                    anchor="c",
                )

            except Exception:
                pdf.setFont(
                    "Helvetica",
                    10,
                )

                pdf.drawString(
                    40,
                    image_top - 30,
                    "Image could not be embedded.",
                )

        else:
            pdf.setFont(
                "Helvetica",
                10,
            )

            pdf.drawString(
                40,
                image_top - 30,
                "Image file not found.",
            )

        y = (
            image_top
            - image_height
            - 30
        )

        # Scene
        y = _draw_paragraph(
            pdf,
            "Scene:",
            panel.get(
                "scene_description",
                "",
            ),
            40,
            y,
            page_width,
        )

        # Caption
        y = _draw_paragraph(
            pdf,
            "Caption:",
            panel.get(
                "caption",
                "",
            ),
            40,
            y,
            page_width,
        )

        # Narration
        y = _draw_paragraph(
            pdf,
            "Narration:",
            panel.get(
                "narration",
                "",
            ),
            40,
            y,
            page_width,
        )

        # Dialogue
        _draw_paragraph(
            pdf,
            "Dialogue:",
            panel.get(
                "dialogue",
                "",
            ),
            40,
            y,
            page_width,
        )

        pdf.showPage()

    pdf.save()

    return f"/export/{filename}"