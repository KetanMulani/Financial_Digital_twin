import json
from typing import Any
from urllib.parse import quote

import httpx

from app.config import Settings, get_settings


class LLMConfigurationError(RuntimeError):
    """The selected provider is unsupported or has no API key."""


class LLMProviderError(RuntimeError):
    """The configured provider failed or returned unusable output."""


class LLMService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.provider = self.settings.llm_provider.strip().lower()

    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:
        if self.provider == "gemini":
            content = self._generate_gemini(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        elif self.provider == "openai":
            content = self._generate_openai(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        elif self.provider == "anthropic":
            content = self._generate_anthropic(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        else:
            raise LLMConfigurationError(
                f"Unsupported LLM provider: {self.provider}"
            )

        return self._decode_json(content)

    def _post(
        self,
        *,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            response = httpx.post(
                url,
                headers=headers,
                params=params,
                json=payload,
                timeout=self.settings.llm_timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
        except httpx.TimeoutException as exc:
            raise LLMProviderError(
                f"{self.provider} request timed out."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise LLMProviderError(
                f"{self.provider} returned HTTP "
                f"{exc.response.status_code}."
            ) from exc
        except (httpx.RequestError, ValueError) as exc:
            raise LLMProviderError(
                f"Could not communicate with {self.provider}."
            ) from exc

        if not isinstance(data, dict):
            raise LLMProviderError(
                f"{self.provider} returned an invalid response."
            )

        return data

    def _generate_gemini(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        api_key = self.settings.gemini_api_key

        if not api_key:
            raise LLMConfigurationError(
                "GEMINI_API_KEY is not configured."
            )

        model = quote(self.settings.gemini_model, safe="")
        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{model}:generateContent"
        )

        data = self._post(
            url=url,
            params={"key": api_key},
            payload={
                "system_instruction": {
                    "parts": [{"text": system_prompt}]
                },
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": user_prompt}],
                    }
                ],
                "generationConfig": {
                    "temperature": 0,
                    "responseMimeType": "application/json",
                },
            },
        )

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError(
                "Gemini returned no usable content."
            ) from exc

    def _generate_openai(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        api_key = self.settings.openai_api_key

        if not api_key:
            raise LLMConfigurationError(
                "OPENAI_API_KEY is not configured."
            )

        data = self._post(
            url="https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            payload={
                "model": self.settings.openai_model,
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
        )

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError(
                "OpenAI returned no usable content."
            ) from exc

    def _generate_anthropic(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        api_key = self.settings.anthropic_api_key

        if not api_key:
            raise LLMConfigurationError(
                "ANTHROPIC_API_KEY is not configured."
            )

        data = self._post(
            url="https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            payload={
                "model": self.settings.anthropic_model,
                "max_tokens": 1200,
                "temperature": 0,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": user_prompt}
                ],
            },
        )

        try:
            return data["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError(
                "Anthropic returned no usable content."
            ) from exc

    @staticmethod
    def _decode_json(content: str) -> dict[str, Any]:
        if not isinstance(content, str) or not content.strip():
            raise LLMProviderError("The LLM returned an empty response.")

        cleaned = content.strip()

        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise LLMProviderError(
                "The LLM returned invalid JSON."
            ) from exc

        if not isinstance(result, dict):
            raise LLMProviderError(
                "The LLM JSON response must be an object."
            )

        return result


llm_service = LLMService()
