"""Black-box tests for the Docker Compose stack or deployed service."""
import os
import uuid

import requests


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
API_KEY = os.getenv("AGENT_API_KEY", "local-e2e-7f72c89f507a4f71ad0cb79d836e7830")


def validate_configuration() -> None:
    if API_KEY.startswith("<") or API_KEY.endswith(">"):
        raise RuntimeError(
            "AGENT_API_KEY is still a placeholder. Set it to the actual Render secret."
        )
    try:
        API_KEY.encode("latin-1")
    except UnicodeEncodeError as exc:
        raise RuntimeError("AGENT_API_KEY must contain only HTTP-header-safe characters.") from exc


validate_configuration()


def headers(user: str | None = None) -> dict[str, str]:
    result = {"X-API-Key": API_KEY}
    if user:
        result["X-User-ID"] = user
    return result


def test_health_and_readiness():
    assert requests.get(f"{BASE_URL}/health", timeout=5).status_code == 200
    assert requests.get(f"{BASE_URL}/ready", timeout=5).status_code == 200


def test_authentication_is_required():
    response = requests.post(f"{BASE_URL}/ask", json={"question": "hello"}, timeout=5)
    assert response.status_code == 401


def test_invalid_input_returns_422():
    response = requests.post(
        f"{BASE_URL}/ask",
        headers=headers(f"invalid-{uuid.uuid4()}"),
        json={"invalid": "data"},
        timeout=5,
    )
    assert response.status_code == 422


def test_conversation_history_is_shared():
    user = f"history-{uuid.uuid4()}"
    first = requests.post(
        f"{BASE_URL}/ask",
        headers=headers(user),
        json={"question": "What is Docker?"},
        timeout=10,
    ).json()
    second = requests.post(
        f"{BASE_URL}/ask",
        headers=headers(user),
        json={"question": "What did I just say?", "session_id": first["session_id"]},
        timeout=10,
    ).json()
    history = requests.get(
        f"{BASE_URL}/sessions/{first['session_id']}", headers=headers(user), timeout=5
    ).json()

    assert second["turn"] == 2
    assert "What is Docker?" in second["answer"]
    assert len(history["messages"]) == 4


def test_rate_limit_is_shared():
    user = f"rate-{uuid.uuid4()}"
    statuses = [
        requests.post(
            f"{BASE_URL}/ask",
            headers=headers(user),
            json={"question": f"request {number}"},
            timeout=10,
        ).status_code
        for number in range(11)
    ]
    assert statuses[-1] == 429
