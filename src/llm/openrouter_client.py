"""OpenRouter LLM client for Guardr"""

from typing import Dict, Any, List, Optional
import requests
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OpenRouterClient:
    """
    OpenRouter API client with fallback providers
    Supports o3-mini, claude-3.5-sonnet, gpt-4o, etc.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout: int = 60,
        default_model: str = "openai/o3-mini",
    ):
        self.api_key = api_key.strip()
        if not self.api_key:
            raise ValueError("OpenRouter API key required")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_model = default_model

    def chat_completion(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False,
        provider_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Send chat completion request to OpenRouter

        Args:
            prompt: User message
            system_prompt: System context
            model: Model to use (defaults to o3-mini)
            temperature: Sampling temperature
            max_tokens: Max output tokens
            stream: Enable streaming (not implemented)
            provider_config: OpenRouter provider preferences

        Returns:
            Response text
        """
        model = model or self.default_model

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        # Default provider config from your curl example
        if provider_config is None:
            provider_config = {
                "allow_fallbacks": True,
                "require_parameters": True,
                "data_collection": "allow",
                "order": ["OpenAI", "Together", "Anthropic"],
            }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "provider": provider_config,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"]
            return content.strip()

        except requests.exceptions.HTTPError as e:
            status = response.status_code
            error_text = response.text if response else "unknown"
            raise RuntimeError(f"OpenRouter HTTP {status}: {error_text}") from e

        except requests.exceptions.Timeout as e:
            raise RuntimeError(f"OpenRouter request timed out after {self.timeout}s") from e

        except Exception as e:
            raise RuntimeError(f"OpenRouter request failed: {e}") from e


__all__ = ["OpenRouterClient"]
