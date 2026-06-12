"""Deterministic, context-aware local LLM substitute used by the deployment lab."""
import time


RESPONSES = {
    "docker": "Docker packages an application and its dependencies into a portable container.",
    "deploy": "Deployment makes an application available on infrastructure where users can access it.",
    "health": "All systems are operational.",
}


def ask(question: str, history: list[dict] | None = None, delay: float = 0.05) -> str:
    time.sleep(delay)
    lowered = question.lower()
    if history and "what did i just say" in lowered:
        previous_questions = [
            message["content"]
            for message in history[:-1]
            if message.get("role") == "user"
        ]
        if previous_questions:
            return f'You previously said: "{previous_questions[-1]}"'
    for keyword, response in RESPONSES.items():
        if keyword in lowered:
            return response
    return "The production AI agent received your question successfully."
