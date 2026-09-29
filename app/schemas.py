from typing import List

from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    story_prompt: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="The basic idea of the comic story.",
    )

    character_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Main character name.",
    )

    setting: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Location or environment of the story.",
    )

    tone: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Tone of the comic.",
    )

    art_style: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Visual art style.",
    )

    @field_validator("*")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty.")

        return value


class Panel(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str

    caption: str = ""
    narration: str = ""
    dialogue: str = ""

    image_path: str = ""


class ComicResponse(BaseModel):
    title: str
    panels: List[Panel]
    pdf_url: str = ""