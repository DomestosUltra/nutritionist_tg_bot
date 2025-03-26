from typing import List
from fastapi import HTTPException
from yandex_cloud_ml_sdk import YCloudML
from .base import LLMService


class YandexService(LLMService):
    def __init__(
        self,
        api_key: str,
        folder_id: str,
        model_name: str = "yandexgpt",
    ) -> None:
        self._sdk = YCloudML(
            auth=api_key,
            folder_id=folder_id,
        )
        self._model = self._sdk.models.completions(
            model_name, model_version="latest"
        )

    async def get_response(self, prompt_query: str, system_prompt: str) -> str:
        messages = [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": prompt_query},
        ]

        try:
            operation = self._model.configure(
                temperature=0.6, max_tokens=2500
            ).run_deferred(messages)

            result = operation.wait()
            return result[0].text

        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Yandex GPT API error: {str(e)}"
            )
