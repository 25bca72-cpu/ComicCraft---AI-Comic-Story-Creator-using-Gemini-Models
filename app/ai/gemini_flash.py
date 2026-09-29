````python
import os
import json

from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_STORY_MODEL", "gemini-2.5-flash")

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_comic_story(prompt: str) -> dict:

    instruction = f"""
Create a short comic story based on this idea:

{prompt}

Return ONLY valid JSON in this exact structure:

{{
    "title": "Comic title",
    "panels": [
        {{
            "panel": 1,
            "scene": "Scene description",
            "narration": "Narration text",
            "dialogue": "Dialogue text"
        }},
        {{
            "panel": 2,
            "scene": "Scene description",
            "narration": "Narration text",
            "dialogue": "Dialogue text"
        }},
        {{
            "panel": 3,
            "scene": "Scene description",
            "narration": "Narration text",
            "dialogue": "Dialogue text"
        }},
        {{
            "panel": 4,
            "scene": "Scene description",
            "narration": "Narration text",
            "dialogue": "Dialogue text"
        }},
        {{
            "panel": 5,
            "scene": "Scene description",
            "narration": "Narration text",
            "dialogue": "Dialogue text"
        }}
    ]
}}

Rules:
- Exactly 5 panels.
- Keep the story connected from panel 1 to panel 5.
- Make the scenes suitable for comic images.
- Keep narration and dialogue short.
- Return only JSON.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=instruction
    )

    text = response.text.strip()

    if text.startswith("```json"):
        text = text[7:]

    if text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    return json.loads(text)
````

**Important:** After pasting, press **Ctrl + S**.

Then tell me **“saved”**. We'll fix the filename next, one step at a time.
