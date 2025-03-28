import httpx
import logging
from .base import LLMService


logger = logging.getLogger(__name__)


class YandexService(LLMService):
    def __init__(self, api_key: str, folder_id: str, model_name: str):
        self.api_key = api_key
        self.folder_id = folder_id
        self.model_name = model_name
        self.base_url = "https://nutromind.ru/yandex-llm"
        self.client = httpx.AsyncClient(http2=True, verify=False)

    async def get_response(
        self, user_query: str, system_prompt: str = ""
    ) -> str:
        try:
            payload = {
                "modelUri": f"gpt://{self.folder_id}/{self.model_name}",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.6,
                    "maxTokens": 2000,
                },
                "messages": [
                    {
                        "role": "system",
                        "text": system_prompt,
                    },
                    {"role": "user", "text": user_query},
                ],
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "x-folder-id": self.folder_id,
                "Content-Type": "application/json",
            }
            logger.debug(f"Sending YandexGPT request: {payload}")
            response = await self.client.post(
                f"{self.base_url}/completion",
                json=payload,
                headers=headers,
                timeout=150,
            )
            response.raise_for_status()
            result = response.json()
            response_text = result["result"]["alternatives"][0]["message"][
                "text"
            ]
            logger.debug(f"YandexGPT response: {response_text}")
            return response_text
        except Exception as e:
            logger.error(f"YandexGPT request failed: {str(e)}")
            raise
