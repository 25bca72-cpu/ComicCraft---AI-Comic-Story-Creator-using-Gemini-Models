from app.services.gemini_service import generate_outline, generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout
from app.services.exporters import save_pdf


async def generate_comic(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> dict:
    """
    Complete ComicCraft generation pipeline.

    1. Generate outline
    2. Generate story narration/dialogue
    3. Generate panel images
    4. Build layout
    5. Export PDF
    """

    # Step 1: Generate 5-panel outline
    panels = generate_outline(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
    )

    # Step 2: Generate narration and dialogue
    panels = generate_story(
        panels=panels,
        story_prompt=story_prompt,
        character_name=character_name,
        tone=tone,
    )

    # Step 3: Generate an image for every panel
    for panel in panels:
        image_path = generate_image(
            prompt=panel.image_prompt,
            panel_number=panel.panel_number,
        )

        panel.image_path = image_path

    # Step 4: Build preview/PDF layout
    layout = build_comic_layout(panels)

    # Step 5: Save PDF
    title = panels[0].title if panels else "ComicCraft Comic"
    pdf_url = save_pdf(
        title=title,
        layout=layout,
    )

    return {
        "panels": panels,
        "layout": layout,
        "pdf_url": pdf_url,
    }

