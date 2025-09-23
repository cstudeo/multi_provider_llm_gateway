"""
Configuration Management

This module handles loading configuration from environment variables
and provides default values for the LLM interface and rate limiter.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
from rate_limiter.limiter import RateLimitConfig

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration"""
    
    # LLM Provider API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Redis Configuration
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    REDIS_DB = int(os.getenv('REDIS_DB', '0'))
    
    # Rate Limiting Configuration
    GLOBAL_RATE_LIMIT = int(os.getenv('GLOBAL_RATE_LIMIT', '100'))
    GLOBAL_WINDOW_SECONDS = int(os.getenv('GLOBAL_WINDOW_SECONDS', '60'))
    OPENAI_RATE_LIMIT = int(os.getenv('OPENAI_RATE_LIMIT', '50'))
    ANTHROPIC_RATE_LIMIT = int(os.getenv('ANTHROPIC_RATE_LIMIT', '30'))
    GOOGLE_RATE_LIMIT = int(os.getenv('GOOGLE_RATE_LIMIT', '20'))
    
    # Flask Configuration
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
    
    @classmethod
    def get_redis_config(cls) -> Dict[str, Any]:
        """Get Redis connection configuration"""
        config = {
            'host': cls.REDIS_HOST,
            'port': cls.REDIS_PORT,
            'db': cls.REDIS_DB,
            'decode_responses': True
        }
        if cls.REDIS_PASSWORD:
            config['password'] = cls.REDIS_PASSWORD
        return config
    
    @classmethod
    def get_rate_limit_configs(cls) -> Dict[str, RateLimitConfig]:
        """Get rate limit configurations for all providers"""
        return {
            'global': RateLimitConfig(
                limit=cls.GLOBAL_RATE_LIMIT,
                window_seconds=cls.GLOBAL_WINDOW_SECONDS,
                key_prefix='global_rate_limit'
            ),
            'openai': RateLimitConfig(
                limit=cls.OPENAI_RATE_LIMIT,
                window_seconds=cls.GLOBAL_WINDOW_SECONDS,
                key_prefix='openai_rate_limit'
            ),
            'anthropic': RateLimitConfig(
                limit=cls.ANTHROPIC_RATE_LIMIT,
                window_seconds=cls.GLOBAL_WINDOW_SECONDS,
                key_prefix='anthropic_rate_limit'
            ),
            'google': RateLimitConfig(
                limit=cls.GOOGLE_RATE_LIMIT,
                window_seconds=cls.GLOBAL_WINDOW_SECONDS,
                key_prefix='google_rate_limit'
            )
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present"""
        required_keys = [
            'OPENAI_API_KEY',
            'ANTHROPIC_API_KEY', 
            'GOOGLE_API_KEY'
        ]
        
        missing_keys = []
        for key in required_keys:
            if not getattr(cls, key):
                missing_keys.append(key)
        
        if missing_keys:
            print(f"Missing required environment variables: {', '.join(missing_keys)}")
            print("Please set these in your .env file or environment")
            return False
        
        return True
