from app.config import settings
from app.schemas import Panel

from app.services.gemini_service import (
    generate_outline,
    generate_story,
)

from app.services.layout_builder import (
    build_comic_layout,
)


def test_demo_outline_has_five_panels(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "demo_mode",
        True,
    )

    panels = generate_outline(
        "A brave fox explores a forest.",
        "Ravi",
        "enchanted forest",
        "funny",
        "comic book",
    )

    assert len(panels) == 5

    assert panels[0].panel_number == 1

    assert panels[-1].panel_number == 5


def test_demo_story_populates_text(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "demo_mode",
        True,
    )

    panels = [
        Panel(
            panel_number=1,
            title="Start",
            scene_description="A forest.",
            image_prompt="A comic forest.",
        )
    ]

    result = generate_story(
        panels,
        "A fox story.",
        "Ravi",
        "funny",
    )

    assert result[0].caption

    assert result[0].narration

    assert result[0].dialogue


def test_layout_builder():
    panels = [
        Panel(
            panel_number=1,
            title="Start",
            scene_description="A forest.",
            image_prompt="Comic forest.",
            caption="A new day.",
            narration="Ravi walks.",
            dialogue="Hello!",
            image_path="/static/panels/a.png",
        )
    ]

    layout = build_comic_layout(
        panels
    )

    assert layout[0]["panel_number"] == 1

    assert (
        layout[0]["image_path"]
        == "/static/panels/a.png"
    )