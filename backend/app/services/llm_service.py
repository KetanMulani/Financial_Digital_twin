import json
from typing import Any

from app.config import get_settings


settings = get_settings()


class LLMService:

    def __init__(self):
        self.provider = settings.llm_provider.lower()

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:

        if self.provider == "gemini":
            return self._generate_gemini(
                system_prompt,
                user_prompt,
            )

        if self.provider == "openai":
            return self._generate_openai(
                system_prompt,
                user_prompt,
            )

        if self.provider == "anthropic":
            return self._generate_anthropic(
                system_prompt,
                user_prompt,
            )

        raise ValueError(
            f"Unsupported LLM provider: {self.provider}"
        )

    def _generate_gemini(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:

        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=settings.gemini_api_key
        )

        prompt = f"""
{system_prompt}

USER REQUEST:
{user_prompt}
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
            ),
        )

        content = response.text

        if not content:
            raise ValueError(
                "Gemini returned an empty response."
            )

        try:
            return json.loads(content)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Gemini returned invalid JSON."
            ) from exc


    def _generate_openai(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:

        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured."
            )

        from openai import OpenAI

        client = OpenAI(
            api_key=settings.openai_api_key
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            response_format={
                "type": "json_object"
            },
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "OpenAI returned an empty response."
            )

        return json.loads(content)

    
llm_service = LLMService()