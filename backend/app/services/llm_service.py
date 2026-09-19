import json
import time
from typing import Any
from urllib.parse import quote

import httpx

from app.config import Settings, get_settings


class LLMConfigurationError(RuntimeError):
    """The selected provider is unsupported or has no API key."""


class LLMProviderError(RuntimeError):
    """The configured provider failed or returned unusable output."""


# Transient failures worth a short retry: rate limiting and the
# provider's own server-side hiccups (Gemini in particular returns
# 503 "model overloaded" fairly often under load).
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_MAX_ATTEMPTS = 3
_RETRY_BACKOFF_SECONDS = 0.6

# A 429 can mean "briefly rate limited, retry shortly" (worth retrying)
# or "quota exhausted for the day/billing period" (retrying is pointless
# until the quota window resets or billing changes). Providers signal the
# latter in the response body rather than with a distinct status code.
_QUOTA_EXHAUSTED_MARKERS = ("resource_exhausted", "quota", "insufficient_quota")


def _is_quota_exhausted(response: httpx.Response) -> bool:
    try:
        body = response.text.lower()
    except Exception:
        return False
    return any(marker in body for marker in _QUOTA_EXHAUSTED_MARKERS)


class LLMService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.provider = self.settings.llm_provider.strip().lower()
        fallback = (self.settings.llm_fallback_provider or "").strip().lower()
        self.fallback_provider = fallback or None

    def _generate_raw(
        self,
        provider: str,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        if provider == "gemini":
            return self._generate_gemini(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        if provider == "openai":
            return self._generate_openai(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        if provider == "anthropic":
            return self._generate_anthropic(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

        raise LLMConfigurationError(
            f"Unsupported LLM provider: {provider}"
        )

    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:
        try:
            content = self._generate_raw(
                self.provider,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        except (LLMConfigurationError, LLMProviderError) as primary_error:
            # The primary provider is unavailable (e.g. a sustained "model
            # overloaded" outage that outlasts our retries). Fall back to a
            # second configured provider rather than failing the request.
            if (
                self.fallback_provider is None
                or self.fallback_provider == self.provider
            ):
                raise

            try:
                content = self._generate_raw(
                    self.fallback_provider,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                )
            except (LLMConfigurationError, LLMProviderError) as fallback_error:
                raise LLMProviderError(
                    f"{self.provider} failed ({primary_error}) and fallback "
                    f"{self.fallback_provider} also failed ({fallback_error})."
                ) from fallback_error

        return self._decode_json(content)

    def _post(
        self,
        *,
        provider: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        last_error: LLMProviderError | None = None

        for attempt in range(1, _MAX_ATTEMPTS + 1):
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
                last_error = LLMProviderError(
                    f"{provider} request timed out."
                )
                last_error.__cause__ = exc
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code

                if status_code == 429 and _is_quota_exhausted(exc.response):
                    last_error = LLMProviderError(
                        f"{provider} quota is exhausted (429). Retrying "
                        "won't help until the quota window resets or "
                        "billing/plan limits are raised."
                    )
                    last_error.__cause__ = exc
                    raise last_error from exc

                last_error = LLMProviderError(
                    f"{provider} returned HTTP {status_code}."
                )
                last_error.__cause__ = exc

                if status_code not in _RETRYABLE_STATUS_CODES:
                    raise last_error from exc
            except (httpx.RequestError, ValueError) as exc:
                last_error = LLMProviderError(
                    f"Could not communicate with {provider}."
                )
                last_error.__cause__ = exc
            else:
                if not isinstance(data, dict):
                    raise LLMProviderError(
                        f"{provider} returned an invalid response."
                    )

                return data

            if attempt < _MAX_ATTEMPTS:
                time.sleep(_RETRY_BACKOFF_SECONDS * attempt)

        assert last_error is not None
        raise last_error

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
            provider="gemini",
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
            provider="openai",
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
            provider="anthropic",
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
