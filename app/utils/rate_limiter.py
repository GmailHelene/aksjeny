import redis
import time
from flask import current_app, has_app_context
from typing import Optional

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, redis_url: Optional[str] = None):
        try:
            self.redis_client = redis.Redis.from_url(redis_url or 'redis://localhost:6379')
        except Exception:
            self.redis_client = None
    
    def is_allowed(self, key: str, max_requests: int, window: int) -> bool:
        """Check if request is allowed based on rate limiting"""
        try:
            if not self.redis_client:
                return True  # Allow if Redis is not available
                
            current_time = int(time.time())
            window_start = current_time - window
            
            # Use Redis sorted set for sliding window
            pipe = self.redis_client.pipeline()
            
            # Remove expired entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests in window
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiry
            pipe.expire(key, window)
            
            results = pipe.execute()
            current_requests = results[1]
            
            return current_requests < max_requests
            
        except Exception as e:
            # Log error only if we have app context
            if has_app_context():
                current_app.logger.error(f"Rate limiter error: {str(e)}")
            return True  # Allow request on error

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(key: str, max_requests: int = 60, window: int = 60) -> bool:
    """Convenience function for rate limiting"""
    return rate_limiter.is_allowed(key, max_requests, window)
