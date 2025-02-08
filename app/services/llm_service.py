from typing import List, Optional, Dict
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.models.chat import Message
from app.core.exceptions import LLMServiceException

settings = get_settings()

class LLMService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def generate_response(
        self,
        message: str,
        history: List[Message],
        context: Optional[Dict] = None
    ) -> str:
        try:
            # Convert history to context string
            context_messages = [
                f"{msg.role}: {msg.content}"
                for msg in history[-5:]  # Only use last 5 messages for context
            ]
            
            system_prompt = "You are an AI assistant helping users on a website."
            if context:
                system_prompt += f"\nWebsite context: {context.get('website_info', '')}."
                system_prompt += f"\nCurrent page: {context.get('current_page', '')}."
            
            # Prepare the prompt
            full_prompt = f"{system_prompt}\n\nChat history:\n"
            full_prompt += "\n".join(context_messages)
            full_prompt += f"\n\nUser: {message}\nAssistant:"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "temperature": self.temperature,
                        "stream": False
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise LLMServiceException(
                        f"Ollama API error: {response.text}"
                    )
                
                return response.json()["response"].strip()
            
        except Exception as e:
            raise LLMServiceException(f"Error generating response: {str(e)}") 