# app/services/chat/api_client.py

from typing import Dict, Any, AsyncGenerator
import httpx
from abc import ABC, abstractmethod

class ApiClient(ABC):
    """API客户端基类"""
    
    @abstractmethod
    async def generate_content(self, payload: Dict[str, Any], model: str, api_key: str) -> Dict[str, Any]:
        pass
        
    @abstractmethod
    async def stream_generate_content(self, payload: Dict[str, Any], model: str, api_key: str) -> AsyncGenerator[str, None]:
        pass

class GeminiApiClient(ApiClient):
    """Gemini API客户端"""
    
    def __init__(self, base_url: str, timeout: int = 300):
        self.base_url = base_url
        self.timeout = timeout
        
    def generate_content(self, payload: Dict[str, Any], model: str, api_key: str) -> Dict[str, Any]:
        timeout = httpx.Timeout(self.timeout, read=self.timeout)
        if model.endswith("-search"):
            model = model[:-7]
        with httpx.Client(timeout=timeout) as client:
            url = f"{self.base_url}/models/{model}:generateContent?key={api_key}"
            response = client.post(url, json=payload)
            if response.status_code != 200:
                error_content = response.text
                raise Exception(f"API call failed with status code {response.status_code}, {error_content}")
            return response.json()
            
    async def stream_generate_content(self, payload: Dict[str, Any], model: str, api_key: str) -> AsyncGenerator[str, None]:
        timeout = httpx.Timeout(self.timeout, read=self.timeout)
        if model.endswith("-search"):
            model = model[:-7]
        async with httpx.AsyncClient(timeout=timeout) as client:
            url = f"{self.base_url}/models/{model}:streamGenerateContent?alt=sse&key={api_key}"
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    error_content = await response.aread()
                    error_msg = error_content.decode("utf-8")
                    raise Exception(f"API call failed with status code {response.status_code}, {error_msg}")
                async for line in response.aiter_lines():
                    yield line
