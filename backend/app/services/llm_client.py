"""
Scoutly — LLM Client (Groq API with retry & backoff)
"""

import json
import time
import asyncio
import logging
from groq import Groq
from app.config import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_RETRIES, LLM_RETRY_BASE_DELAY

logger = logging.getLogger(__name__)


class LLMClient:
    """Wrapper around Groq API with exponential backoff retry logic."""

    def __init__(self):
        if not GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set — LLM calls will fail")
        self.client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
        self.model = LLM_MODEL
        self.temperature = LLM_TEMPERATURE
        self.max_retries = LLM_MAX_RETRIES
        self.retry_base_delay = LLM_RETRY_BASE_DELAY

    async def call(
        self,
        system_prompt: str,
        user_payload: str | dict,
        temperature: float | None = None,
        json_mode: bool = True,
    ) -> dict | str:
        """
        Call the LLM with retry logic.

        Args:
            system_prompt: System-level instructions for the LLM
            user_payload: User message (string or dict → serialized to JSON)
            temperature: Override default temperature
            json_mode: If True, force JSON output format

        Returns:
            Parsed JSON dict if json_mode, else raw string
        """
        if not self.client:
            raise RuntimeError("LLM client not initialized — set GROQ_API_KEY")

        if isinstance(user_payload, dict):
            user_content = json.dumps(user_payload, default=str)
        else:
            user_content = str(user_payload)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        last_error = None

        for attempt in range(self.max_retries):
            try:
                # Run synchronous Groq call in thread pool
                response = await asyncio.to_thread(
                    self.client.chat.completions.create, **kwargs
                )

                content = response.choices[0].message.content

                if json_mode:
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError as e:
                        logger.error(f"LLM returned invalid JSON: {e}")
                        logger.debug(f"Raw content: {content[:500]}")
                        # Try to extract JSON from the response
                        return self._extract_json(content)
                else:
                    return content

            except Exception as e:
                last_error = e
                error_str = str(e)
                is_rate_limit = "429" in error_str or "rate_limit" in error_str.lower()
                is_server_error = "500" in error_str or "503" in error_str

                if is_rate_limit or is_server_error:
                    delay = self.retry_base_delay * (2 ** attempt)
                    logger.warning(
                        f"LLM call failed (attempt {attempt + 1}/{self.max_retries}): {error_str}. "
                        f"Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"LLM call failed with non-retryable error: {error_str}")
                    raise

        logger.error(f"LLM call failed after {self.max_retries} retries")
        raise last_error

    def _extract_json(self, text: str) -> dict:
        """Try to extract a JSON object from text that might have extra content."""
        # Look for JSON between curly braces
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

        # Look for JSON array
        start = text.find("[")
        end = text.rfind("]") + 1
        if start != -1 and end > start:
            try:
                return {"items": json.loads(text[start:end])}
            except json.JSONDecodeError:
                pass

        # Give up — return raw text wrapped in dict
        return {"raw_response": text}


# Singleton instance
llm_client = LLMClient()
