import json
import re
from typing import Any

from app.config import settings
from app.schemas import Panel


def _extract_json(text: str) -> Any:
    """
    Extract JSON from Gemini response.

    Gemini may sometimes return JSON inside
    markdown code fences, so those fences are removed.
    """

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.I
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        # Try to find JSON array.
        start = text.find("[")
        end = text.rfind("]")

        if start != -1 and end != -1:

            return json.loads(
                text[start:end + 1]
            )

        # Try to find JSON object.
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1:

            return json.loads(
                text[start:end + 1]
            )

        raise ValueError(
            "Gemini did not return valid JSON."
        )


def _client():

    if not settings.gemini_api_key:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Add it to .env or enable DEMO_MODE."
        )

    from google import genai

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> list[Panel]:

    if settings.demo_mode:

        return _demo_outline(
            story_prompt,
            character_name,
            setting,
            tone,
            art_style
        )

    prompt = f"""
Create a cohesive {settings.panel_count}-panel comic outline.

Story idea:
{story_prompt}

Main character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

Return ONLY valid JSON.

Return an array with exactly
{settings.panel_count} objects.

Each object must contain:

panel_number
title
scene_description
image_prompt

The five panels should have:

1. Beginning
2. Development
3. Turning point
4. Climax
5. Ending

Keep the character appearance and
visual identity consistent.

Do not include markdown code fences.
"""

    client = _client()

    response = client.models.generate_content(
        model=settings.gemini_outline_model,
        contents=prompt,
    )

    data = _extract_json(response.text)

    if not isinstance(data, list):

        raise ValueError(
            "Outline JSON must be a list."
        )

    panels = []

    for i, item in enumerate(
        data[:settings.panel_count],
        start=1
    ):

        panels.append(
            Panel(
                panel_number=i,
                title=str(
                    item.get(
                        "title",
                        f"Panel {i}"
                    )
                ),
                scene_description=str(
                    item.get(
                        "scene_description",
                        ""
                    )
                ),
                image_prompt=str(
                    item.get(
                        "image_prompt",
                        ""
                    )
                ),
            )
        )

    if len(panels) != settings.panel_count:

        raise ValueError(
            f"Expected {settings.panel_count} "
            f"panels, received {len(panels)}."
        )

    return panels


def generate_story(
    panels: list[Panel],
    story_prompt: str,
    character_name: str,
    tone: str,
) -> list[Panel]:

    if settings.demo_mode:

        return _demo_story(
            panels,
            character_name,
            tone
        )

    outline_json = json.dumps(
        [
            panel.model_dump()
            for panel in panels
        ],
        ensure_ascii=False
    )

    prompt = f"""
Expand this comic outline into
polished narration and dialogue.

Original story:

{story_prompt}

Main character:

{character_name}

Tone:

{tone}

Outline:

{outline_json}

Return ONLY valid JSON.

Return exactly
{settings.panel_count} objects.

Every object must contain:

panel_number
caption
narration
dialogue

Keep the original plot and panel order.

Dialogue must be short enough
for a comic panel.

Do not use markdown fences.
"""

    client = _client()

    response = client.models.generate_content(
        model=settings.gemini_story_model,
        contents=prompt,
    )

    data = _extract_json(response.text)

    if not isinstance(data, list):

        raise ValueError(
            "Story JSON must be a list."
        )

    by_number = {
        int(
            item.get(
                "panel_number",
                i + 1
            )
        ): item
        for i, item in enumerate(data)
    }

    for i, panel in enumerate(
        panels,
        start=1
    ):

        item = by_number.get(
            i,
            {}
        )

        panel.caption = str(
            item.get(
                "caption",
                ""
            )
        )

        panel.narration = str(
            item.get(
                "narration",
                ""
            )
        )

        panel.dialogue = str(
            item.get(
                "dialogue",
                ""
            )
        )

    return panels


def _demo_outline(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style
):

    beats = [

        (
            "The Beginning",
            f"{character_name} starts "
            "an unexpected adventure."
        ),

        (
            "A New Discovery",
            f"{character_name} discovers "
            "something unusual."
        ),

        (
            "The Challenge",
            f"A difficult problem appears "
            f"in {setting}."
        ),

        (
            "The Turning Point",
            f"{character_name} finds "
            "a clever way forward."
        ),

        (
            "A New Dawn",
            f"{character_name} finishes "
            "the adventure with hope."
        ),
    ]

    panels = []

    for i, (title, description) in enumerate(
        beats,
        start=1
    ):

        panels.append(
            Panel(
                panel_number=i,
                title=title,
                scene_description=description,
                image_prompt=(
                    f"comic book illustration, "
                    f"{art_style}, "
                    f"{setting}, "
                    f"main character "
                    f"{character_name}, "
                    f"{description}, "
                    f"consistent character design, "
                    f"cinematic composition"
                ),
            )
        )

    return panels


def _demo_story(
    panels,
    character_name,
    tone
):

    for panel in panels:

        panel.caption = (
            f"{panel.title} — "
            f"{tone.title()} mood."
        )

        panel.narration = (
            f"{character_name} moves "
            "through the scene, "
            "determined to discover "
            "what happens next."
        )

        panel.dialogue = (
            f"{character_name}: "
            "I can do this!"
        )

    return panels