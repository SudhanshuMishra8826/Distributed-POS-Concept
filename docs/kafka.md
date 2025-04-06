# Kafka Setup and Testing

This document provides detailed instructions for setting up and testing the Kafka environment in the Distributed POS system.

## Services Overview

### Zookeeper
- **Purpose**: Manages Kafka cluster coordination
- **Port**: 2181
- **Access**: localhost:2181

### Kafka
- **Purpose**: Message broker for handling distributed events
- **Port**: 9092
- **Access**: localhost:9092

### Kafdrop
- **Purpose**: Web UI for Kafka management
- **Port**: 9001
- **Access**: http://localhost:9001

## Setup Instructions

1. Start all services:
```bash
docker compose up
```

2. Verify services are running:
```bash
docker compose ps
```
Expected containers:
- distributed-pos-concept-zookeeper-1
- distributed-pos-concept-kafka-1
- distributed-pos-concept-kafdrop-1

## Testing Steps

### 1. Command Line Testing

1. Create a test topic:
```bash
docker compose exec kafka kafka-topics --create --topic test-topic --bootstrap-server localhost:29092 --partitions 1 --replication-factor 1
```

2. List all topics:
```bash
docker compose exec kafka kafka-topics --list --bootstrap-server localhost:29092
```

3. Start a consumer (in a new terminal):
```bash
docker compose exec kafka kafka-console-consumer --topic test-topic --bootstrap-server localhost:29092 --from-beginning
```

4. Produce messages (in another terminal):
```bash
docker compose exec kafka kafka-console-producer --topic test-topic --bootstrap-server localhost:29092
```
Type some messages and press Enter after each message.

### 2. Kafdrop UI Testing

1. Open http://localhost:9001 in your browser

2. Verify the setup:
   - Click "Brokers" to see Kafka broker status
   - Click "Topics" to see your test-topic
   - Click on test-topic to view messages
   - Click "Consumer Groups" to see active consumers

## Clean Up

To stop all services:
```bash
docker compose down
```

## Troubleshooting

1. Port Conflicts:
   - Check if ports 2181, 9092, or 9001 are in use
   - Modify port mappings in docker-compose.yaml if needed

2. Service Issues:
   - Check logs: `docker compose logs`
   - Ensure sufficient Docker resources
   - Clean up: `docker compose down -v`

## Additional Resources

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Kafdrop GitHub](https://github.com/obsidiandynamics/kafdrop)
- [Docker Compose Documentation](https://docs.docker.com/compose/) 