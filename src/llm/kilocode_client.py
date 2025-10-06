"""Kilocode LLM client utilities."""

from __future__ import annotations

from typing import Any, Dict, List

from src.utils.logger import get_logger

try:  # pragma: no cover - optional dependency
    import requests
    from requests.exceptions import RequestException
except ImportError:  # pragma: no cover - handled gracefully
    requests = None  # type: ignore
    RequestException = Exception  # type: ignore[misc, assignment]


logger = get_logger(__name__)


class KilocodeClient:
    """Simple HTTP client for the Kilocode Chat Completions API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.kilocode.com/v1",
        timeout: int = 30,
    ) -> None:
        if requests is None:  # pragma: no cover - safety guard
            raise RuntimeError("Requests library is required for KilocodeClient")

        self.api_key = api_key.strip()
        if not self.api_key:
            raise ValueError("Kilocode API key must be provided")

        self.base_url = base_url.rstrip("/") or "https://api.kilocode.com/v1"
        self.timeout = timeout

    def chat_completion(
        self,
        prompt: str,
        *,
        system_prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Send a chat completion request and return the response content."""

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        data = self._post_json("/chat/completions", payload)
        return self._extract_message_content(data.get("choices"))

    def _post_json(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if requests is None:  # pragma: no cover - safety guard
            raise RuntimeError("Requests library is unavailable")

        url = f"{self.base_url}{path}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
        except RequestException as exc:
            raise RuntimeError(f"Kilocode request failed: {exc}") from exc

        try:
            response.raise_for_status()
        except RequestException as exc:
            status = getattr(response, "status_code", "unknown")
            text = getattr(response, "text", "")
            raise RuntimeError(f"Kilocode HTTP {status}: {text}") from exc

        try:
            return response.json()
        except ValueError as exc:
            raise RuntimeError("Kilocode returned a non-JSON response") from exc

    def _extract_message_content(self, choices: Any) -> str:
        if not choices:
            return ""

        first_choice: Any
        if isinstance(choices, list):
            first_choice = choices[0] if choices else {}
        else:
            first_choice = choices

        if isinstance(first_choice, dict):
            message = first_choice.get("message", first_choice)
        else:
            message = first_choice

        if isinstance(message, dict):
            content: Any = message.get("content", "")
        else:
            content = message or ""

        if isinstance(content, list):
            logger.warning(
                "Kilocode API response content is a list; coercing to string for processing.",
            )
            content = "".join(str(part) for part in content)

        return str(content).strip()


__all__: List[str] = ["KilocodeClient"]
