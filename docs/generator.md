# Event Generator Documentation

## Overview
The Event Generator is a Python application that simulates Point of Sale (POS) transactions by generating and publishing events to a Kafka topic. It creates realistic transaction sequences that include employee login, basket creation, customer identification, item additions, subtotal calculation, payment processing, and employee logout.

## Features
- Generates realistic POS transaction sequences
- Publishes events to Kafka in real-time
- Configurable delay between transaction sequences
- Simulates multiple types of events with realistic data
- Maintains state between events in a sequence
- Uses Faker library for generating realistic test data

## Event Types
The generator produces the following types of events:

1. **Employee Login** (`employee_login`)
   - Employee ID
   - Terminal ID
   - Timestamp

2. **Basket Start** (`basket_started`)
   - Basket ID
   - Employee ID
   - Timestamp

3. **Customer Identification** (`customer_identified`)
   - Customer ID
   - Basket ID
   - Timestamp

4. **Item Addition** (`item_added`)
   - Item ID
   - Basket ID
   - Quantity
   - Price
   - Timestamp

5. **Subtotal Calculation** (`subtotal_calculated`)
   - Basket ID
   - Subtotal
   - Tax
   - Timestamp

6. **Payment** (`payment_completed`)
   - Basket ID
   - Amount
   - Payment Method
   - Timestamp

7. **Employee Logout** (`employee_logout`)
   - Employee ID
   - Terminal ID
   - Timestamp

## Configuration
The generator can be configured using environment variables:

- `KAFKA_BOOTSTRAP_SERVERS`: Comma-separated list of Kafka brokers (default: "localhost:9092")
- `KAFKA_TOPIC`: Kafka topic name (default: "pos_events")
- `DELAY_BETWEEN_SEQUENCES`: Delay in seconds between transaction sequences (default: 5.0)

## Dependencies
- kafka-python==1.4.7
- python-dotenv==0.19.2
- pydantic==1.10.13
- faker==18.13.0
- pytest==7.4.3
- pytest-cov==4.1.0

## Usage
1. Set up the environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Configure environment variables (optional):
   ```bash
   export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
   export KAFKA_TOPIC=pos_events
   export DELAY_BETWEEN_SEQUENCES=5.0
   ```

3. Run the generator:
   ```bash
   python main.py
   ```

## Transaction Sequence
Each transaction sequence follows this order:
1. Employee login
2. Basket creation
3. Customer identification
4. Item additions (2-4 random items)
5. Subtotal calculation
6. Payment processing
7. Employee logout

## Sample Items
The generator includes a predefined set of items:
- Milk ($3.99)
- Bread ($2.49)
- Eggs ($4.99)
- Beer ($8.99)
- Wine ($15.99)

## Error Handling
- The generator includes error handling for missing prerequisites (e.g., no employees logged in)
- Exceptions are caught and logged during sequence generation
- The generator can be safely interrupted with Ctrl+C

## Development
The codebase is organized into three main files:
- `main.py`: Entry point and configuration
- `generator.py`: Core event generation logic
- `models.py`: Pydantic models for event types

