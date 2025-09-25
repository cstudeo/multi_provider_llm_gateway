"""
Base LLM Client Interface

This module defines the abstract base class for all LLM providers,
ensuring a unified interface across different providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


# Standardized response format for all LLM providers
class LLMResponse(BaseModel):
    content: str
    provider: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


# Standardized request format for all LLM providers
class LLMRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    
    class Config:
        extra = "allow"


# Abstract base class for LLM providers - all implementations must inherit from this
class BaseLLMClient(ABC):
    
    def __init__(self,api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        pass
    
    @abstractmethod
    def get_default_model(self) -> str:
        pass
