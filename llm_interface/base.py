"""
Base LLM Client Interface

This module defines the abstract base class for all LLM providers,
ensuring a unified interface across different providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class LLMResponse(BaseModel):
    """Standardized response format for all LLM providers"""
    content: str
    provider: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMRequest(BaseModel):
    """Standardized request format for all LLM providers"""
    prompt: str
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    
    class Config:
        extra = "allow"


class BaseLLMClient(ABC):
    """
    Abstract base class for LLM providers.
    
    All provider implementations must inherit from this class
    and implement the generate method.
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the LLM client.
        
        Args:
            api_key: API key for the provider
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            request: Standardized request object
            
        Returns:
            Standardized response object
            
        Raises:
            Exception: If the request fails
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of the provider.
        
        Returns:
            Provider name string
        """
        pass
    
    @abstractmethod
    def get_default_model(self) -> str:
        """
        Get the default model for this provider.
        
        Returns:
            Default model name
        """
        pass
