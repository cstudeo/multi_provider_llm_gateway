"""
Anthropic Provider Implementation
"""

import anthropic
from typing import Dict, Any
from .base import BaseLLMClient, LLMRequest, LLMResponse


class AnthropicClient(BaseLLMClient):
    """Anthropic provider implementation"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.default_model = kwargs.get('default_model', 'claude-3-sonnet-20240229')
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Anthropic API"""
        try:
            model = request.model or self.default_model
            
            # Extract additional parameters from request
            extra_params = {k: v for k, v in request.dict().items() 
                           if k not in ['prompt', 'model', 'max_tokens', 'temperature']}
            
            response = self.client.messages.create(
                model=model,
                max_tokens=request.max_tokens or 1000,
                temperature=request.temperature,
                messages=[{"role": "user", "content": request.prompt}],
                **extra_params
            )
            
            return LLMResponse(
                content=response.content[0].text,
                provider="anthropic",
                model=model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                } if response.usage else None,
                metadata={
                    "stop_reason": response.stop_reason,
                    "stop_sequence": response.stop_sequence
                }
            )
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def get_provider_name(self) -> str:
        return "anthropic"
    
    def get_default_model(self) -> str:
        return self.default_model
