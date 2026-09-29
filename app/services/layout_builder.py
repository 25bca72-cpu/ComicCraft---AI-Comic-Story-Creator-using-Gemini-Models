from app.schemas import Panel


def build_comic_layout(
    panels: list[Panel],
) -> list[dict]:
    """
    Organize generated panels into a layout structure.

    Each dictionary contains the information needed
    by the preview page and PDF exporter.
    """

    layout = []

    for panel in panels:
        layout.append(
            {
                "panel_number": panel.panel_number,
                "title": panel.title,
                "image_path": panel.image_path,
                "scene_description": panel.scene_description,
                "image_prompt": panel.image_prompt,
                "caption": panel.caption,
                "narration": panel.narration,
                "dialogue": panel.dialogue,
            }
        )

    return layout