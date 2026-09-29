from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


client = TestClient(app)


def test_health():
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_home():
    response = client.get("/")

    assert response.status_code == 200

    assert "ComicCraft" in response.text


def test_generate_in_demo_mode(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "demo_mode",
        True,
    )

    response = client.post(
        "/generate-comic/json",
        json={
            "story_prompt": (
                "A brave fox explores "
                "an enchanted forest."
            ),
            "character_name": "Ravi",
            "setting": "enchanted forest",
            "tone": "dramatic",
            "art_style": "comic book",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["panels"]) == 5

    assert data["pdf_url"].startswith(
        "/export/"
    )