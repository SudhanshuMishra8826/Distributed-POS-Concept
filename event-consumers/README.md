# Event Consumers

This directory contains event consumer plugins for the Distributed POS system. Each plugin is responsible for processing specific types of events from the Kafka message queue.

## Plugin Status Check

Each plugin now includes a status check mechanism that verifies if the plugin is active before processing events. This ensures that inactive plugins don't consume resources or process events unnecessarily.

### How It Works

1. Before processing an event, each plugin checks its status using the following process:
   - First, it checks Redis for a cached status using the key `service:{plugin_id}`
   - If the status is not found in Redis, it falls back to checking the API at `/services/status/{plugin_id}`
   - If the plugin is inactive, it logs a warning and skips processing the event

2. The status check is implemented in two utility modules:
   - `utils.py` for Python plugins
   - `utils.js` for JavaScript plugins

### Implementation Details

#### Python Plugins

```python
# Check if the plugin is active
if not check_plugin_status(PLUGIN_ID):
    log_plugin_inactive(PLUGIN_ID, event)
    return
```

#### JavaScript Plugins

```javascript
// Check if the plugin is active
const isActive = await checkPluginStatus(PLUGIN_ID);
if (!isActive) {
    logPluginInactive(PLUGIN_ID, event);
    return;
}
```

## Available Plugins

- **age-verification**: Monitors item added events and determines if age verification is required
- **fraud-detection**: Monitors payment events and detects high-value transactions
- **customer-lookup**: Looks up customer information for events
- **purchase-recommender**: Recommends products based on purchase history
- **employee-tracker**: Tracks employee activities

## Running the Plugins

Each plugin can be run independently. Follow the instructions in each plugin's README file for specific setup and running instructions.

### Python Plugins

```bash
cd <plugin-directory>
pip install -r requirements.txt
python plugin.py
```

### JavaScript Plugins

```bash
cd <plugin-directory>
npm install
npm start
```

## Environment Variables

Each plugin requires certain environment variables to be set. These are typically defined in a `.env` file in each plugin's directory. Common variables include:

- `KAFKA_BROKER`: Comma-separated list of Kafka brokers (default: localhost:9092)
- `REDIS_HOST`: Redis host (default: localhost)
- `REDIS_PORT`: Redis port (default: 6379)
- `REDIS_PASSWORD`: Redis password (if required)
- `API_BASE_URL`: Base URL for the plugin management API (default: http://localhost:8000) 