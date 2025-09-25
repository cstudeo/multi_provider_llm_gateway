"""
LLM Service

This module provides a unified service that integrates multiple LLM providers
with distributed rate limiting capabilities.
"""

import redis
from typing import Dict, Optional, List, Any
from llm_interface.base import BaseLLMClient, LLMRequest, LLMResponse
from llm_interface.openai_client import OpenAIClient
from llm_interface.anthropic_client import AnthropicClient
from llm_interface.google_client import GoogleClient
from rate_limiter.limiter import DistributedRateLimiter, RateLimitExceededException
from config import Config


class LLMService:
    """
    This service provides:
    - Unified interface to multiple LLM providers
    - Distributed rate limiting across providers
    """
    
    def __init__(self):
        """Initialize the LLM service with all providers and rate limiter"""
        self.providers: Dict[str, BaseLLMClient] = {}
        self.rate_limiter: Optional[DistributedRateLimiter] = None
        self._initialize_providers()
        self._initialize_rate_limiter()
    
    def _initialize_providers(self):
        """Initialize all available LLM providers"""
        try:
            self.providers['openai'] = OpenAIClient()
            self.providers['anthropic'] = AnthropicClient()            
            self.providers['google'] = GoogleClient()                
        except Exception as e:
            print(f"Error initializing providers: {e}")
    
    def _initialize_rate_limiter(self):
        """Initialize the distributed rate limiter"""
        try:
            redis_client = redis.Redis(**Config.get_redis_config())
            redis_client.ping()
            
            rate_limit_configs = Config.get_rate_limit_configs()
            self.rate_limiter = DistributedRateLimiter(redis_client, rate_limit_configs)
            print("Distributed rate limiter initialized")
            
        except Exception as e:
            print(f"Warning: Rate limiter initialization failed: {e}")
            print("Continuing without rate limiting...")
            self.rate_limiter = None
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return list(self.providers.keys())
    
    def generate(
        self, 
        provider: str, 
        prompt: str, 
        user_id: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response using the specified provider with rate limiting.
        """
        if provider not in self.providers:
            available = ', '.join(self.get_available_providers())
            raise ValueError(f"Provider '{provider}' not available. Available providers: {available}")
        
        # Apply rate limiting
        if self.rate_limiter:
            self._check_rate_limits(provider, user_id)
        
        # Create request and generate response
        request = LLMRequest(prompt=prompt, **kwargs)
        response = self.providers[provider].generate(request)
        
        return response
        """
        Generate a response with automatic failover to other providers.
        
        Args:
            preferred_provider: Preferred provider to try first
            prompt: The input prompt
            user_id: Optional user identifier for rate limiting
            **kwargs: Additional parameters for the LLM request
            
        Returns:
            LLMResponse object
            
        Raises:
            Exception: If all providers fail
        """
        providers_to_try = [preferred_provider] + [
            p for p in self.get_available_providers() if p != preferred_provider
        ]
        
        last_error = None
        
        for provider in providers_to_try:
            try:
                return self.generate(provider, prompt, user_id, **kwargs)
            except RateLimitExceededException:
                # Don't failover on rate limit - this is expected behavior
                raise
            except Exception as e:
                print(f"Provider {provider} failed: {e}")
                last_error = e
                continue
        
        raise Exception(f"All providers failed. Last error: {last_error}")
    
    def _check_rate_limits(self, provider: str, user_id: Optional[str] = None):
        """Check rate limits for global and provider-specific limits"""
        if not self.rate_limiter:
            return
        
        # Check global rate limit
        global_key = f"global:{user_id}" if user_id else "global"
        is_allowed, global_info = self.rate_limiter.is_allowed(global_key, 'global')
        
        if not is_allowed:
            raise RateLimitExceededException(
                f"Global rate limit exceeded. Limit: {global_info['limit']}/minute",
                global_info
            )
        
        # Check provider-specific rate limit
        provider_key = f"{provider}:{user_id}" if user_id else provider
        is_allowed, provider_info = self.rate_limiter.is_allowed(provider_key, provider)
        
        if not is_allowed:
            raise RateLimitExceededException(
                f"Provider '{provider}' rate limit exceeded. Limit: {provider_info['limit']}/minute",
                provider_info
            )
    
    def get_rate_limit_status(self, provider: str, user_id: Optional[str] = None) -> Dict[str, Dict[str, int]]:
        """
        Get current rate limit status for a provider and user.
        """
        if not self.rate_limiter:
            return {}
        
        status = {}
        
        # Global rate limit status
        global_key = f"global:{user_id}" if user_id else "global"
        status['global'] = self.rate_limiter.get_status(global_key, 'global')
        
        # Provider-specific rate limit status
        provider_key = f"{provider}:{user_id}" if user_id else provider
        status[provider] = self.rate_limiter.get_status(provider_key, provider)
        
        return status
