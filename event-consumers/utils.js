/**
 * Utility functions for event consumer plugins
 */

const axios = require('axios');
const Redis = require('ioredis');

// Configure logging
const log = {
    info: (message) => console.log(`[INFO] ${new Date().toISOString()} - ${message}`),
    warn: (message) => console.log(`[WARN] ${new Date().toISOString()} - ${message}`),
    error: (message) => console.log(`[ERROR] ${new Date().toISOString()} - ${message}`),
    debug: (message) => console.log(`[DEBUG] ${new Date().toISOString()} - ${message}`)
};

// Redis configuration
const REDIS_CONFIG = {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379'),
    password: process.env.REDIS_PASSWORD || '',
    decodeResponses: true
};

// API configuration
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

/**
 * Get a connection to Redis
 * @returns {Redis} Redis client
 */
function getRedisConnection() {
    try {
        return new Redis(REDIS_CONFIG);
    } catch (error) {
        log.error(`Redis connection error: ${error.message}`);
        return null;
    }
}

/**
 * Check if a plugin is active by first checking Redis cache,
 * then falling back to the API if needed.
 * 
 * @param {string} pluginId - The ID of the plugin to check
 * @returns {Promise<boolean>} - True if the plugin is active, False otherwise
 */
async function checkPluginStatus(pluginId) {
    // Try to get from Redis first
    const redis = getRedisConnection();
    if (redis) {
        try {
            const cachedStatus = await redis.get(`service:${pluginId}`);
            if (cachedStatus) {
                return cachedStatus === 'active';
            }
        } catch (error) {
            log.error(`Redis error when checking plugin status: ${error.message}`);
        } finally {
            redis.quit();
        }
    }

    // If not in Redis or Redis error, check API
    try {
        const response = await axios.get(`${API_BASE_URL}/services/status/${pluginId}`);
        if (response.status === 200) {
            return response.data.status === 'active';
        } else {
            log.warn(`Plugin ${pluginId} not found or error: ${response.status}`);
            return false;
        }
    } catch (error) {
        log.error(`API error when checking plugin status: ${error.message}`);
        return false;
    }
}

/**
 * Log that a plugin is inactive and an event was not processed
 * 
 * @param {string} pluginId - The ID of the inactive plugin
 * @param {Object} eventData - Optional event data that was not processed
 */
function logPluginInactive(pluginId, eventData = null) {
    const eventInfo = eventData ? `Event data: ${JSON.stringify(eventData)}` : 'No event data';
    log.warn(`Plugin '${pluginId}' is inactive. Event not processed. ${eventInfo}`);
}

module.exports = {
    checkPluginStatus,
    logPluginInactive
}; 