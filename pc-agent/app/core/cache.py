"""Redis caching layer for performance optimization."""
import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
import redis
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class CacheManager:
    """Redis cache manager."""
    
    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {str(e)}. Caching disabled.")
            self.redis_client = None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"pcbuild:{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            logger.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        if not self.redis_client:
            return False
        
        try:
            ttl = ttl or settings.REDIS_CACHE_TTL
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            logger.debug(f"Cache delete: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(f"pcbuild:{pattern}*")
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} cache keys matching {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
            return 0


cache = CacheManager()


def cached(prefix: str, ttl: Optional[int] = None):
    """
    Decorator to cache function results (supports both sync and async).
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds (optional)
    """
    def decorator(func: Callable) -> Callable:
        import asyncio
        from inspect import iscoroutinefunction
        
        if iscoroutinefunction(func):
            # Async version
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = cache._generate_key(prefix, *args, **kwargs)
                
                # Try to get from cache
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute async function
                result = await func(*args, **kwargs)
                
                # Store in cache
                cache.set(cache_key, result, ttl)
                
                return result
            
            return async_wrapper
        else:
            # Sync version
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = cache._generate_key(prefix, *args, **kwargs)
                
                # Try to get from cache
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Store in cache
                cache.set(cache_key, result, ttl)
                
                return result
            
            return sync_wrapper
    return decorator


def invalidate_cache(pattern: str):
    """Invalidate cache entries matching pattern."""
    return cache.clear_pattern(pattern)

