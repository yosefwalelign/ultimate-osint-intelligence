"""Caching System for OSINT Results"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching for OSINT operations"""
    
    def __init__(self, redis_url: str = None, ttl_hours: int = 24):
        """Initialize cache manager"""
        self.redis_url = redis_url
        self.ttl = timedelta(hours=ttl_hours)
        self.cache_store = {}  # In-memory cache (replace with Redis)
        logger.info(f"Cache initialized with TTL: {ttl_hours} hours")
    
    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> bool:
        """Set cache value"""
        try:
            ttl = ttl or self.ttl
            self.cache_store[key] = {
                'value': value,
                'expires_at': datetime.now() + ttl
            }
            logger.debug(f"Cache set: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get cache value"""
        try:
            if key not in self.cache_store:
                return None
            
            item = self.cache_store[key]
            if datetime.now() > item['expires_at']:
                del self.cache_store[key]
                return None
            
            logger.debug(f"Cache hit: {key}")
            return item['value']
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete cache entry"""
        try:
            if key in self.cache_store:
                del self.cache_store[key]
                logger.debug(f"Cache deleted: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        try:
            self.cache_store.clear()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'total_entries': len(self.cache_store),
            'ttl_hours': int(self.ttl.total_seconds() / 3600)
        }
