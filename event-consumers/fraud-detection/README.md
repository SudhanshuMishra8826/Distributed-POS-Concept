# Fraud Detection Plugin

This plugin monitors events from the POS system and detects potential fraudulent activity based on configured rules. It maintains state across multiple events to identify patterns that might indicate fraud.

## Features

- Listens for events on the `pos_events` Kafka topic
- Maintains state of events for each customer/basket in Redis
- Detects fraudulent activity based on configurable rules
- Publishes fraud alerts back to the `pos_events` topic
- Handles graceful shutdown on SIGINT and SIGTERM signals

## Fraud Detection Rules

The plugin includes several pre-configured fraud detection rules:

1. **High Value Transaction**
   - Detects transactions with unusually high values (> $1000)
   - Severity: Medium

2. **Rapid Transactions**
   - Detects multiple transactions (3+) in a short time period (< 5 minutes)
   - Severity: High

3. **Suspicious Item Combination**
   - Detects suspicious combinations of items (e.g., 3+ gift cards)
   - Severity: Medium

4. **Customer Mismatch**
   - Detects when customer data doesn't match the transaction pattern
   - Example: Gold tier customer making very small transactions
   - Severity: Low

5. **Multiple Payment Methods**
   - Detects when multiple payment methods are used in a short time
   - Severity: Medium

## Requirements

- Node.js 14+
- Kafka
- Redis

## Installation

1. Install dependencies:

```bash
npm install
```

2. Create a `.env` file with the following configuration:

```env
KAFKA_BROKER=localhost:9092
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
EVENT_WINDOW_SIZE=100
TIME_WINDOW_SECONDS=3600
```

## Usage

Run the plugin:

```bash
node plugin.js
```

The plugin will:
1. Connect to Kafka and Redis using the configuration from the `.env` file
2. Listen for events on the `pos_events` topic
3. Store events in Redis for each customer/basket
4. Check for fraudulent activity based on the configured rules
5. Publish fraud alerts back to the `pos_events` topic

## Testing

To test the plugin, run the test events generator:

```bash
node test-events.js
```

This will generate various test scenarios that trigger the fraud detection rules:

- Normal transaction
- High-value transaction
- Rapid transactions
- Suspicious item combination
- Customer mismatch
- Multiple payment methods

## Event Format

### Input Events

The plugin listens for various event types on the `pos_events` topic:

```json
{
  "event_type": "customer_identified",
  "customer_id": "12345",
  "basket_id": "67890",
  "timestamp": "2025-04-06T20:09:09+05:30"
}
```

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

```json
{
  "event_type": "item_added",
  "basket_id": "67890",
  "item_id": "ITEM001",
  "item_name": "Laptop",
  "quantity": 1,
  "price": 999.99,
  "timestamp": "2025-04-06T20:09:09+05:30"
}
```

```json
{
  "event_type": "payment_processed",
  "basket_id": "67890",
  "amount": 999.99,
  "payment_method": "credit_card",
  "timestamp": "2025-04-06T20:09:09+05:30"
}
```

```json
{
  "event_type": "transaction_completed",
  "basket_id": "67890",
  "items": [
    {
      "id": "ITEM001",
      "name": "Laptop",
      "price": 999.99,
      "category": "Electronics",
      "quantity": 1
    }
  ],
  "amount": 999.99,
  "timestamp": "2025-04-06T20:09:09+05:30"
}
```

### Output Events (Fraud Alerts)

```json
{
  "event_type": "fraud_alert",
  "alert_id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_id": "12345",
  "basket_id": "67890",
  "rule_id": "high-value-transaction",
  "rule_name": "High Value Transaction",
  "rule_description": "Detects transactions with unusually high values",
  "severity": "medium",
  "action": "alert",
  "timestamp": "2025-04-06T20:09:09+05:30",
  "events": [
    {
      "event_type": "transaction_completed",
      "timestamp": "2025-04-06T20:09:09+05:30"
    }
  ]
}
```

## Configuration

The plugin can be configured using environment variables:

- `KAFKA_BROKER`: Kafka broker address (default: localhost:9092)
- `REDIS_HOST`: Redis host (default: localhost)
- `REDIS_PORT`: Redis port (default: 6379)
- `REDIS_PASSWORD`: Redis password (default: empty)
- `EVENT_WINDOW_SIZE`: Number of events to keep in memory (default: 100)
- `TIME_WINDOW_SECONDS`: Time window for events in seconds (default: 3600)

## Troubleshooting

Common issues:

1. **Kafka Connection Error**
   - Ensure Kafka is running and accessible
   - Check the `KAFKA_BROKER` setting in `.env`

2. **Redis Connection Error**
   - Ensure Redis is running and accessible
   - Check the Redis settings in `.env`

3. **Node.js Package Issues**
   - Try reinstalling dependencies: `npm install` 