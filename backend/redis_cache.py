import gzip
import logging
import os
import pickle
from functools import wraps
from pathlib import Path
from typing import Any, Callable

import redis
from dotenv import load_dotenv

# Load env variables immediately
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RedisCache:
    def __init__(self):
        self.redis_client = None
        self.enabled = False
        self._connect()

    def _connect(self):
        """Establish connection to Redis."""
        try:
            redis_url = os.getenv("REDIS_URL")

            if redis_url:
                # Use connection string if available
                self.redis_client = redis.from_url(redis_url, decode_responses=False)
                # Mask password in logs
                safe_url = redis_url.split("@")[-1] if "@" in redis_url else redis_url
                logger.info(f"✅ Connected to Redis at {safe_url}")
            else:
                # Fallback to individual variables
                host = os.getenv("REDIS_HOST", "localhost")
                port = int(os.getenv("REDIS_PORT", 6379))
                username = os.getenv("REDIS_USERNAME", None)
                password = os.getenv("REDIS_PASSWORD", None)

                # Construct connection args
                kwargs = {
                    "host": host,
                    "port": port,
                    "decode_responses": False,  # We want bytes for pickling
                }

                if username:
                    kwargs["username"] = username
                if password:
                    kwargs["password"] = password

                self.redis_client = redis.Redis(**kwargs)
                logger.info(f"✅ Connected to Redis at {host}:{port}")

            # Test connection
            self.redis_client.ping()
            self.enabled = True

        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Caching will be disabled.")
            self.enabled = False

    def get(self, key: str) -> Any:
        """Retrieve and deserialize a value from Redis (handling compression)."""
        if not self.enabled or not self.redis_client:
            return None

        try:
            data = self.redis_client.get(key)
            if data:
                try:
                    # Try decompressing first
                    data = gzip.decompress(data)
                except (gzip.BadGzipFile, OSError):
                    # Fallback for legacy uncompressed data
                    pass
                return pickle.loads(data)
        except Exception as e:
            logger.error(f"Error retrieving from Redis key {key}: {e}")

        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Serialize, compress, and store a value in Redis with TTL."""
        if not self.enabled or not self.redis_client:
            return False

        try:
            data = pickle.dumps(value)
            compressed_data = gzip.compress(data)
            return self.redis_client.setex(key, ttl, compressed_data)
        except Exception as e:
            logger.error(f"Error setting Redis key {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching a pattern."""
        if not self.enabled or not self.redis_client:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing pattern {pattern}: {e}")
            return 0


# Global instance
redis_cache = RedisCache()


def cache_with_redis(ttl_seconds: int = 300, prefix: str = "cache"):
    """Decorator to cache function results in Redis."""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not redis_cache.enabled:
                return func(*args, **kwargs)

            # Create a unique key based on args
            # Clean args to ensure they are string-convertible
            clean_args = [str(a) for a in args]
            clean_kwargs = {k: str(v) for k, v in kwargs.items()}

            # Sort kwargs for consistency
            sorted_kwargs = sorted(clean_kwargs.items())

            # Build key: prefix:func_name:arg1:arg2...
            key_parts = (
                [prefix, func.__name__]
                + clean_args
                + [f"{k}={v}" for k, v in sorted_kwargs]
            )
            cache_key = ":".join(key_parts)

            # Check cache
            cached_result = redis_cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result

            # Execute and cache
            result = func(*args, **kwargs)
            redis_cache.set(cache_key, result, ttl=ttl_seconds)
            logger.debug(f"Cache set for {cache_key}")
            return result

        return wrapper

    return decorator
