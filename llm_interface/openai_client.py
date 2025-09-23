"""
OpenAI Provider Implementation
"""

import openai
from typing import Dict, Any
from .base import BaseLLMClient, LLMRequest, LLMResponse


class OpenAIClient(BaseLLMClient):
    """OpenAI provider implementation"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = openai.OpenAI(api_key=api_key)
        self.default_model = kwargs.get('default_model', 'gpt-3.5-turbo')
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenAI API"""
        try:
            model = request.model or self.default_model
            
            extra_params = {k: v for k, v in request.dict().items() 
                           if k not in ['prompt', 'model', 'max_tokens', 'temperature']}
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": request.prompt}],
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                **extra_params
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                provider="openai",
                model=model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "created": response.created
                }
            )
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def get_provider_name(self) -> str:
        return "openai"
    
    def get_default_model(self) -> str:
        return self.default_model
