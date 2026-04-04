"""
GeminiClient is a client for interacting with the Gemini API to generate content based on system 
and user prompts. It handles the construction of the request payload, making the HTTP 
request, and processing the response to extract the generated content. The client also 
includes error handling for HTTP errors and cases where the response does not contain 
valid candidates or text.
"""
from __future__ import annotations

import httpx

from app.core.config import Settings
from app.core.exceptions import ExternalServiceError


class GeminiClient:
    """
    GeminiClient is responsible for communicating with the Gemini API to generate content 
    based on provided prompts and configuration. It checks for API key availability, constructs 
    the request payload, sends the request, and processes the response to extract the generated 
    content. It also handles errors that may occur during the HTTP request or if the response 
    does not contain valid data.
    """
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.timeout = settings.http_timeout_seconds

    async def is_available(self) -> bool:
        """
        Checks if the Gemini API is available by verifying that the API key is set in the settings.
        """
        return bool(self.settings.gemini_api_key)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_output_tokens: int,
    ) -> str:
        """
        Generates content using the Gemini API based on the provided system and user prompts,
        temperature, and maximum output tokens. It constructs the request payload, sends the 
        request,and processes the response to extract the generated content. If any errors 
        occur during the request or if the response does not contain valid candidates or 
        text, it raises an ExternalServiceError with an appropriate message.
        """
        model = self.settings.gemini_model
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={self.settings.gemini_api_key}"
        )

        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_output_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(f"Gemini request failed: {exc}") from exc

        candidates = data.get("candidates", [])
        if not candidates:
            raise ExternalServiceError("Gemini returned no candidates")

        parts = candidates[0].get("content", {}).get("parts", [])
        texts = [p.get("text", "") for p in parts if "text" in p]
        output = "\n".join(texts).strip()

        if not output:
            raise ExternalServiceError("Gemini returned an empty response")

        return output
