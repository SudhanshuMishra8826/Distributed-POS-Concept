# Customer Lookup Plugin

This plugin listens for customer identification events from a POS system, retrieves customer data from a cache or remote system, and publishes customer data events back to Kafka.

## Features

- Listens for `customer_identified` events on the `pos_events` Kafka topic
- Retrieves customer data from Redis cache first
- Falls back to remote system if data is not in cache
- Uses default data if remote system is unavailable
- Publishes `customer_data` events back to Kafka
- Handles graceful shutdown on SIGINT and SIGTERM signals

## Requirements

- Python 3.8+
- Kafka
- Redis

## Installation

1. Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following configuration:

```env
KAFKA_BROKER=localhost:9092
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

## Usage

1. Make sure your virtual environment is activated
2. Run the plugin:

```bash
# Option 1: Using python directly
python plugin.py

# Option 2: Using the executable script
./plugin.py
```

The plugin will:
1. Connect to Kafka and Redis using the configuration from the `.env` file
2. Listen for `customer_identified` events on the `pos_events` topic
3. Process each event by looking up customer data
4. Publish `customer_data` events back to the `pos_events` topic

## Event Format

### Input Event (customer_identified)

```json
{
  "event_type": "customer_identified",
  "customer_id": "12345",
  "basket_id": "67890",
  "timestamp": "2025-04-06T20:09:09+05:30"
}
```

### Output Event (customer_data)

```json
{
  "event_type": "customer_data",
  "customer_id": "12345",
  "basket_id": "67890",
  "customer_data": {
    "customer_id": "12345",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "+1234567890",
    "membership_tier": "Gold",
    "points": 1000,
    "last_visit": "2025-04-06T20:09:09+05:30"
  },
  "timestamp": "2025-04-06T20:09:09+05:30"
}
```

## Development

To modify the plugin:

1. Make your changes to `plugin.py`
2. Test the changes
3. Update the README if necessary

## Troubleshooting

Common issues:

1. **Kafka Connection Error**
   - Ensure Kafka is running and accessible
   - Check the `KAFKA_BROKER` setting in `.env`

2. **Redis Connection Error**
   - Ensure Redis is running and accessible
   - Check the Redis settings in `.env`

3. **Python Package Issues**
   - Ensure you're in the virtual environment
   - Try reinstalling dependencies: `pip install -r requirements.txt` 