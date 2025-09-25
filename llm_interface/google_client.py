"""
Google Provider Implementation
"""

import google.generativeai as genai
from typing import Dict, Any
from .base import BaseLLMClient, LLMRequest, LLMResponse
from config import Config


class GoogleClient(BaseLLMClient):
    """Google provider implementation"""

    def __init__(self, **kwargs):
        api_key = Config.GOOGLE_API_KEY
        super().__init__(api_key, **kwargs)
        genai.configure(api_key=api_key)
        self.default_model = kwargs.get('default_model', 'gemini-1.5-pro')
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Google Gemini API"""
        try:
            model_name = request.model or self.default_model
            model = genai.GenerativeModel(model_name)
            
            generation_config = {}
            if request.max_tokens:
                generation_config['max_output_tokens'] = request.max_tokens
            if request.temperature is not None:
                generation_config['temperature'] = request.temperature
            
            extra_params = {k: v for k, v in request.dict().items() 
                           if k not in ['prompt', 'model', 'max_tokens', 'temperature']}
            
            response = model.generate_content(
                request.prompt,
                generation_config=generation_config,
                **extra_params
            )
            
            usage_data = None
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage_data = {
                    "prompt_token_count": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "candidates_token_count": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_token_count": getattr(response.usage_metadata, 'total_token_count', 0)
                }
            
            return LLMResponse(
                content=response.text,
                provider="google",
                model=model_name,
                usage=usage_data,
                metadata={
                    "finish_reason": getattr(response, 'finish_reason', None),
                    "safety_ratings": [rating.__dict__ for rating in getattr(response, 'safety_ratings', [])] if hasattr(response, 'safety_ratings') else []
                }
            )
        except Exception as e:
            raise Exception(f"Google API error: {str(e)}")
    
    def get_provider_name(self) -> str:
        return "google"
    
    def get_default_model(self) -> str:
        return self.default_model
