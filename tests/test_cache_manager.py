import pytest
import time
from unittest.mock import patch, MagicMock
from app.utils.cache_manager import CacheManager, cached, cache_manager

@pytest.fixture
def test_cache():
    """Create a test cache manager"""
    return CacheManager('redis://localhost:6379/2')  # Use test database

class TestCacheManager:
    def test_set_and_get(self, test_cache):
        """Test basic cache set and get operations"""
        key = 'test_key'
        value = {'data': 'test_value', 'number': 42}
        
        # Set value
        result = test_cache.set(key, value, ttl=60)
        assert result is True
        
        # Get value
        retrieved_value = test_cache.get(key)
        assert retrieved_value == value
    
    def test_get_nonexistent_key(self, test_cache):
        """Test getting a non-existent key"""
        result = test_cache.get('nonexistent_key')
        assert result is None
    
    def test_delete(self, test_cache):
        """Test cache deletion"""
        key = 'test_delete_key'
        value = 'test_value'
        
        # Set value
        test_cache.set(key, value)
        
        # Verify it exists
        assert test_cache.get(key) == value
        
        # Delete it
        result = test_cache.delete(key)
        assert result is True
        
        # Verify it's gone
        assert test_cache.get(key) is None
    
    def test_ttl_expiration(self, test_cache):
        """Test TTL expiration"""
        key = 'test_ttl_key'
        value = 'test_value'
        
        # Set with short TTL
        test_cache.set(key, value, ttl=1)
        
        # Should exist immediately
        assert test_cache.get(key) == value
        
        # Wait for expiration
        time.sleep(2)
        
        # Should be expired
        assert test_cache.get(key) is None
    
    def test_clear_pattern(self, test_cache):
        """Test pattern-based cache clearing"""
        # Set multiple keys
        test_cache.set('user:1:profile', {'name': 'User 1'})
        test_cache.set('user:2:profile', {'name': 'User 2'})
        test_cache.set('other:data', {'value': 'test'})
        
        # Clear user pattern
        deleted_count = test_cache.clear_pattern('user:*')
        assert deleted_count >= 2  # Should delete at least the user keys
        
        # Verify user keys are gone
        assert test_cache.get('user:1:profile') is None
        assert test_cache.get('user:2:profile') is None
        
        # Verify other key still exists
        assert test_cache.get('other:data') is not None
    
    def test_cache_stats(self, test_cache):
        """Test cache statistics"""
        # Perform some operations
        test_cache.set('key1', 'value1')
        test_cache.get('key1')  # Hit
        test_cache.get('nonexistent')  # Miss
        
        stats = test_cache.get_stats()
        
        assert 'hits' in stats
        assert 'misses' in stats
        assert 'hit_rate' in stats
        assert 'sets' in stats
        assert stats['hits'] >= 1
        assert stats['misses'] >= 1

class TestCacheDecorators:
    def test_cached_decorator(self, test_cache):
        """Test the @cached decorator"""
        call_count = 0
        
        @cached(ttl=60)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # First call should execute function
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1
        
        # Second call should use cache
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # Should not increment
        
        # Different parameters should execute function again
        result3 = expensive_function(2, 3)
        assert result3 == 5
        assert call_count == 2

if __name__ == '__main__':
    pytest.main([__file__])
