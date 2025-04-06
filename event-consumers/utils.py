import redis
import requests
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Redis configuration
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'decode_responses': True
}

# API configuration
API_BASE_URL = 'http://localhost:8000'

def get_redis_connection():
    """Get a connection to Redis"""
    try:
        return redis.Redis(**REDIS_CONFIG)
    except redis.RedisError as e:
        logger.error(f"Redis connection error: {str(e)}")
        return None

def check_plugin_status(plugin_id: str) -> bool:
    """
    Check if a plugin is active by first checking Redis cache,
    then falling back to the API if needed.
    
    Args:
        plugin_id: The ID of the plugin to check
        
    Returns:
        bool: True if the plugin is active, False otherwise
    """
    # Try to get from Redis first
    redis_client = get_redis_connection()
    if redis_client:
        try:
            cached_status = redis_client.get(f"service:{plugin_id}")
            if cached_status:
                return cached_status == "active"
        except redis.RedisError as e:
            logger.error(f"Redis error when checking plugin status: {str(e)}")
    
    # If not in Redis or Redis error, check API
    try:
        response = requests.get(f"{API_BASE_URL}/services/status/{plugin_id}")
        if response.status_code == 200:
            status_data = response.json()
            return status_data.get("status") == "active"
        else:
            logger.warning(f"Plugin {plugin_id} not found or error: {response.status_code}")
            return False
    except requests.RequestException as e:
        logger.error(f"API error when checking plugin status: {str(e)}")
        return False

def log_plugin_inactive(plugin_id: str, event_data: Optional[dict] = None):
    """
    Log that a plugin is inactive and an event was not processed
    
    Args:
        plugin_id: The ID of the inactive plugin
        event_data: Optional event data that was not processed
    """
    event_info = f"Event data: {event_data}" if event_data else "No event data"
    logger.warning(f"Plugin '{plugin_id}' is inactive. Event not processed. {event_info}") 