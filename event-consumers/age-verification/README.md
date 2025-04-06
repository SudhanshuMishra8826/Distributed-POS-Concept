# Age Verification Plugin

This plugin monitors item added events from the POS system and determines if age verification is required when certain items are purchased.

## Features

- Monitors `item_added` events from the POS system
- Checks if the item ID requires age verification
- Publishes `age_verification_required` events when age-restricted items are added to a basket
- Currently focuses on beer and wine items only

## Age-Restricted Items

The plugin currently checks for the following age-restricted items:

| Item ID | Item Name | Minimum Age | Description |
|---------|-----------|-------------|-------------|
| 004 | Beer | 21 | Beer item |
| 005 | Wine | 21 | Wine item |

## Requirements

- Python 3.8+
- Kafka
- Redis

## Installation

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file with the following settings:

```
KAFKA_BROKER=localhost:9092
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

## Usage

1. Start the plugin:
   ```
   python plugin.py
   ```

2. The plugin will listen for `item_added` events on the `pos_events` topic.

3. When an age-restricted item is added to a basket, the plugin will publish an `age_verification_required` event.

## Event Formats

### Input Event: item_added

```json
{
  "event_type": "item_added",
  "customer_id": "customer-123",
  "basket_id": "basket-456",
  "item": {
    "id": "004",
    "name": "Beer",
    "price": 8.99
  },
  "timestamp": "2023-04-06T12:34:56.789Z"
}
```

### Output Event: age_verification_required

```json
{
  "event_type": "age_verification_required",
  "verification_id": "verification-123",
  "customer_id": "customer-123",
  "basket_id": "basket-456",
  "min_age": 21,
  "item_id": "004",
  "item_name": "Beer",
  "timestamp": "2023-04-06T12:34:57.123Z",
  "original_event": {
    "event_type": "item_added",
    "timestamp": "2023-04-06T12:34:56.789Z"
  }
}
```

## Testing

To test the plugin, you can use the provided test script:

```
python send-test-event.py
```

This will send test events for various items, including beer, wine, and non-restricted items.

## Development

To add new age-restricted items, update the `AGE_RESTRICTED_ITEM_IDS` dictionary in the `plugin.py` file.

## Troubleshooting

- If the plugin is not receiving events, check that Kafka is running and accessible.
- If the plugin is not publishing events, check that the Kafka producer is configured correctly.
- Check the logs for any error messages. 