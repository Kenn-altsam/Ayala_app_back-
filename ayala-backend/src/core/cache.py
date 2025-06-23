import json
import pickle
from typing import Any, Optional, Union
from functools import wraps
import redis.asyncio as redis
from .config import settings

# Redis client instance
redis_client: Optional[redis.Redis] = None


async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    print("ℹ️  Redis is disabled for now")
    redis_client = None
    # Uncomment below to enable Redis
    # redis_client = redis.from_url(settings.REDIS_URL, decode_responses=False)
    # try:
    #     await redis_client.ping()
    #     print("✅ Redis connected successfully")
    # except Exception as e:
    #     print(f"❌ Redis connection failed: {e}")
    #     redis_client = None


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()


async def get_cache(key: str) -> Any:
    """Get value from cache"""
    if not redis_client:
        return None
    
    try:
        data = await redis_client.get(key)
        if data:
            return pickle.loads(data)
    except Exception as e:
        print(f"Cache get error: {e}")
    
    return None


async def set_cache(key: str, value: Any, expire: int = 3600) -> bool:
    """Set value in cache with expiration time (default 1 hour)"""
    if not redis_client:
        return False
    
    try:
        serialized_data = pickle.dumps(value)
        await redis_client.setex(key, expire, serialized_data)
        return True
    except Exception as e:
        print(f"Cache set error: {e}")
        return False


async def delete_cache(key: str) -> bool:
    """Delete key from cache"""
    if not redis_client:
        return False
    
    try:
        await redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Cache delete error: {e}")
        return False


async def clear_cache_pattern(pattern: str) -> int:
    """Clear all keys matching pattern"""
    if not redis_client:
        return 0
    
    try:
        keys = await redis_client.keys(pattern)
        if keys:
            return await redis_client.delete(*keys)
        return 0
    except Exception as e:
        print(f"Cache clear pattern error: {e}")
        return 0


def cache_result(key_prefix: str, expire: int = 3600):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{key_prefix}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache first
            cached_result = await get_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await set_cache(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator 