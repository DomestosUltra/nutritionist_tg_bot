from typing import List, Any, Union, Protocol


class LLMService(Protocol):
    llm_client: Union[Any]
    model: str

    async def get_response(
        self, prompt_query: str, system_prompt: str
    ) -> None:
        raise NotImplementedError
