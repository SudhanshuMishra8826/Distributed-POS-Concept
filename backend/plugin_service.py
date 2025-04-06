from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import mysql.connector
from mysql.connector import Error
import redis
import json
from datetime import timedelta

app = FastAPI(title="Plugin Management Service")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'pos_user',
    'password': 'password',
    'database': 'pos_db'
}

# Redis configuration
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'decode_responses': True
}

# Cache expiration time (24 hours)
CACHE_EXPIRATION = timedelta(hours=24)

# Pydantic models for request/response
class PluginBase(BaseModel):
    id: str
    active: bool
    filters: Optional[Dict[str, Any]] = None
    actions: Optional[Dict[str, Any]] = None

class PluginUpdate(BaseModel):
    active: Optional[bool] = None
    filters: Optional[Dict[str, Any]] = None
    actions: Optional[Dict[str, Any]] = None

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

def get_redis_connection():
    try:
        return redis.Redis(**REDIS_CONFIG)
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis connection error: {str(e)}")

def cache_service_status(service_name: str, status: str):
    """Cache service status in Redis"""
    try:
        redis_client = get_redis_connection()
        redis_client.setex(
            f"service:{service_name}",
            CACHE_EXPIRATION,
            status
        )
    except (redis.RedisError, HTTPException) as e:
        print(f"Redis caching error: {str(e)}")
        # Continue execution even if caching fails

def get_cached_service_status(service_name: str) -> Optional[str]:
    """Get service status from Redis cache"""
    try:
        redis_client = get_redis_connection()
        return redis_client.get(f"service:{service_name}")
    except (redis.RedisError, HTTPException) as e:
        print(f"Redis cache retrieval error: {str(e)}")
        return None

def clear_service_cache(service_name: str):
    """Clear service status from Redis cache"""
    try:
        redis_client = get_redis_connection()
        redis_client.delete(f"service:{service_name}")
    except (redis.RedisError, HTTPException) as e:
        print(f"Redis cache clearing error: {str(e)}")
        # Continue execution even if cache clearing fails

@app.post("/plugins/", response_model=PluginBase)
async def register_plugin(plugin: PluginBase):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        query = """
        INSERT INTO plugins (id, active, filters, actions)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (
            plugin.id,
            plugin.active,
            json.dumps(plugin.filters) if plugin.filters else None,
            json.dumps(plugin.actions) if plugin.actions else None
        ))
        connection.commit()
        
        # Cache the service status
        cache_service_status(plugin.id, "active" if plugin.active else "inactive")
        
        return plugin
    except Error as e:
        raise HTTPException(status_code=400, detail=f"Error registering plugin: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@app.put("/plugins/{plugin_id}", response_model=PluginBase)
async def update_plugin(plugin_id: str, plugin_update: PluginUpdate):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # First check if plugin exists
        cursor.execute("SELECT * FROM plugins WHERE id = %s", (plugin_id,))
        existing_plugin = cursor.fetchone()
        if not existing_plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")
        
        # Parse JSON strings in existing plugin
        if existing_plugin.get('filters'):
            existing_plugin['filters'] = json.loads(existing_plugin['filters'])
        if existing_plugin.get('actions'):
            existing_plugin['actions'] = json.loads(existing_plugin['actions'])
        
        # Build update query dynamically based on provided fields
        update_fields = []
        params = []
        if plugin_update.active is not None:
            update_fields.append("active = %s")
            params.append(plugin_update.active)
        if plugin_update.filters is not None:
            update_fields.append("filters = %s")
            params.append(json.dumps(plugin_update.filters))
        if plugin_update.actions is not None:
            update_fields.append("actions = %s")
            params.append(json.dumps(plugin_update.actions))
        
        if not update_fields:
            return existing_plugin
        
        query = f"UPDATE plugins SET {', '.join(update_fields)} WHERE id = %s"
        params.append(plugin_id)
        
        cursor.execute(query, tuple(params))
        connection.commit()
        
        # Fetch and return updated plugin
        cursor.execute("SELECT * FROM plugins WHERE id = %s", (plugin_id,))
        updated_plugin = cursor.fetchone()
        
        # Parse JSON strings in updated plugin
        if updated_plugin.get('filters'):
            updated_plugin['filters'] = json.loads(updated_plugin['filters'])
        if updated_plugin.get('actions'):
            updated_plugin['actions'] = json.loads(updated_plugin['actions'])
        
        # Update cache with new status if active field was updated
        if plugin_update.active is not None:
            cache_service_status(plugin_id, "active" if updated_plugin['active'] else "inactive")
        
        return updated_plugin
    except Error as e:
        raise HTTPException(status_code=400, detail=f"Error updating plugin: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@app.get("/plugins/", response_model=List[PluginBase])
async def list_plugins():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM plugins")
        plugins = cursor.fetchall()
        
        # Parse JSON strings into dictionaries for each plugin
        for plugin in plugins:
            if plugin.get('filters'):
                plugin['filters'] = json.loads(plugin['filters'])
            if plugin.get('actions'):
                plugin['actions'] = json.loads(plugin['actions'])
            
            # Update cache with current status
            cache_service_status(plugin['id'], "active" if plugin['active'] else "inactive")
            
        return plugins
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching plugins: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@app.get("/plugins/{plugin_id}", response_model=PluginBase)
async def get_plugin(plugin_id: str):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM plugins WHERE id = %s", (plugin_id,))
        plugin = cursor.fetchone()
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")
        
        # Parse JSON strings into dictionaries
        if plugin.get('filters'):
            plugin['filters'] = json.loads(plugin['filters'])
        if plugin.get('actions'):
            plugin['actions'] = json.loads(plugin['actions'])
        
        # Update cache with current status
        cache_service_status(plugin_id, "active" if plugin['active'] else "inactive")
        
        return plugin
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching plugin: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@app.delete("/plugins/{plugin_id}")
async def delete_plugin(plugin_id: str):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("DELETE FROM plugins WHERE id = %s", (plugin_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Plugin not found")
        
        connection.commit()
        
        # Clear cache
        clear_service_cache(plugin_id)
        
        return {"message": f"Plugin {plugin_id} deleted successfully"}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error deleting plugin: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@app.get("/services/status/{service_name}")
async def get_service_status(service_name: str):
    """Get the status of a service from cache or database"""
    # Try to get from cache first
    cached_status = get_cached_service_status(service_name)
    if cached_status:
        return {"service": service_name, "status": cached_status}
    
    # If not in cache, check database
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT active FROM plugins WHERE id = %s", (service_name,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Service not found")
        
        status = "active" if result['active'] else "inactive"
        
        # Cache the status
        cache_service_status(service_name, status)
        
        return {"service": service_name, "status": status}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching service status: {str(e)}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 