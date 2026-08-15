import logging
from openai import OpenAI
from app.core.config import settings
from openai import OpenAI
from langsmith.wrappers import wrap_openai
from langsmith import traceable

logger = logging.getLogger(__name__)


class LLMService:

    _client: OpenAI | None = None

    @classmethod
    def _get_client(cls) -> OpenAI:
        """Lazy initialization for OpenAI client."""
        if cls._client is None:
            cls._client = wrap_openai(OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.OPENROUTER_API_KEY,
            ))
        return cls._client

    @classmethod
    def _get_models(cls, task_type: str) -> tuple[str, str]:
        if task_type == "routing":
            return settings.FAST_MODEL, settings.FAST_FALLBACK_MODEL
        return settings.HEAVY_MODEL, settings.HEAVY_FALLBACK_MODEL

    @classmethod
    @traceable(name="OpenRouter", run_type="llm")
    def _call_api(cls, model: str, messages: list, temperature: float) -> str:
        logger.info(f"Using model: {model}")

        response = cls._get_client().chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            timeout=60,
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(f"Empty response from model: {model}")

        return content

    @classmethod
    def generate(
        cls,
        prompt: str,
        task_type: str = "analysis",
        system_prompt: str | None = None,
        temperature: float = 0.2,
    ) -> str:

        primary_model, fallback_model = cls._get_models(task_type)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            return cls._call_api(primary_model, messages, temperature)

        except Exception as e:
            logger.warning(f"Primary model '{primary_model}' failed: {e}")

            try:
                return cls._call_api(fallback_model, messages, temperature)

            except Exception as fallback_error:
                logger.exception("Fallback model failed.")

                raise RuntimeError(
                    f"\nBoth models failed.\n\n"
                    f"Primary ({primary_model}):\n{e}\n\n"
                    f"Fallback ({fallback_model}):\n{fallback_error}\n"
                )