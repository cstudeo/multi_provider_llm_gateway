"""
Distributed Rate Limiter Implementation

This module implements a distributed rate limiter using Redis with sliding window
counter algorithm for accurate rate limiting across multiple processes and servers.
"""

import redis
import time
import json
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    limit: int
    window_seconds: int
    key_prefix: str = "rate_limit"


class DistributedRateLimiter:
    """
    Distributed rate limiter using Redis with sliding window counter algorithm.
    
    This implementation provides:
    - Atomic operations using Redis Lua scripts
    - Sliding window for accurate rate limiting
    - Support for multiple rate limit keys (global, per-provider, etc.)
    - Fault tolerance with Redis connection handling
    """
    
    def __init__(self, redis_client: redis.Redis, configs: Dict[str, RateLimitConfig]):
        """
        Initialize the rate limiter.
        
        Args:
            redis_client: Redis client instance
            configs: Dictionary mapping rate limit keys to their configurations
        """
        self.redis = redis_client
        self.configs = configs
        
        self.lua_script = """
        local key = KEYS[1]
        local window = tonumber(ARGV[1])
        local limit = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        
        -- Clean up old entries
        redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
        
        -- Count current requests
        local current = redis.call('ZCARD', key)
        
        if current < limit then
            -- Add new request
            redis.call('ZADD', key, now, now .. ':' .. math.random())
            redis.call('EXPIRE', key, window)
            return {1, current + 1, limit - current - 1}
        else
            return {0, current, 0}
        end
        """
        self.lua_script_hash = None
    
    def _load_lua_script(self) -> str:
        """Load the Lua script into Redis and return its hash"""
        if self.lua_script_hash is None:
            self.lua_script_hash = self.redis.script_load(self.lua_script)
        return self.lua_script_hash
    
    def is_allowed(self, key: str, config_name: str) -> Tuple[bool, Dict[str, int]]:
        """
        Check if a request is allowed under the rate limit.
        
        Args:
            key: Unique identifier for the rate limit (e.g., 'global', 'openai:user123')
            config_name: Name of the rate limit configuration to use
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
            rate_limit_info contains: current_count, limit, remaining, reset_time
        """
        if config_name not in self.configs:
            raise ValueError(f"Unknown rate limit configuration: {config_name}")
        
        config = self.configs[config_name]
        redis_key = f"{config.key_prefix}:{key}"
        
        try:
            script_hash = self._load_lua_script()
            result = self.redis.evalsha(
                script_hash,
                1,
                redis_key,
                config.window_seconds,
                config.limit,
                int(time.time() * 1000)
            )
            
            is_allowed = bool(result[0])
            current_count = result[1]
            remaining = result[2]
            
            reset_time = int(time.time()) + config.window_seconds
            
            return is_allowed, {
                'current_count': current_count,
                'limit': config.limit,
                'remaining': remaining,
                'reset_time': reset_time
            }
            
        except redis.RedisError as e:
            print(f"Redis error in rate limiter: {e}")
            return True, {
                'current_count': 0,
                'limit': config.limit,
                'remaining': config.limit,
                'reset_time': int(time.time()) + config.window_seconds
            }
    
    def get_status(self, key: str, config_name: str) -> Dict[str, int]:
        """
        Get current rate limit status without consuming a request.
        
        Args:
            key: Unique identifier for the rate limit
            config_name: Name of the rate limit configuration
            
        Returns:
            Dictionary with current rate limit status
        """
        if config_name not in self.configs:
            raise ValueError(f"Unknown rate limit configuration: {config_name}")
        
        config = self.configs[config_name]
        redis_key = f"{config.key_prefix}:{key}"
        
        try:
            now = int(time.time() * 1000)
            
            # Clean up old entries and count current
            self.redis.zremrangebyscore(redis_key, 0, now - (config.window_seconds * 1000))
            current_count = self.redis.zcard(redis_key)
            
            remaining = max(0, config.limit - current_count)
            reset_time = int(time.time()) + config.window_seconds
            
            return {
                'current_count': current_count,
                'limit': config.limit,
                'remaining': remaining,
                'reset_time': reset_time
            }
            
        except redis.RedisError as e:
            print(f"Redis error getting rate limit status: {e}")
            return {
                'current_count': 0,
                'limit': config.limit,
                'remaining': config.limit,
                'reset_time': int(time.time()) + config.window_seconds
            }
    
    def reset(self, key: str, config_name: str) -> bool:
        """
        Reset the rate limit for a given key.
        
        Args:
            key: Unique identifier for the rate limit
            config_name: Name of the rate limit configuration
            
        Returns:
            True if reset was successful
        """
        if config_name not in self.configs:
            raise ValueError(f"Unknown rate limit configuration: {config_name}")
        
        config = self.configs[config_name]
        redis_key = f"{config.key_prefix}:{key}"
        
        try:
            self.redis.delete(redis_key)
            return True
        except redis.RedisError as e:
            print(f"Redis error resetting rate limit: {e}")
            return False


class RateLimitExceededException(Exception):
    """Exception raised when rate limit is exceeded"""
    
    def __init__(self, message: str, rate_limit_info: Dict[str, int]):
        super().__init__(message)
        self.rate_limit_info = rate_limit_info
