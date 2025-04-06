# Distributed POS System - Kafka Setup

This project sets up a Kafka environment with Zookeeper and Kafdrop UI for the Distributed POS system.

## Services

- **Zookeeper**: Manages Kafka cluster coordination
- **Kafka**: Message broker for handling distributed events
- **Kafdrop**: Web UI for Kafka management

## Quick Start

1. Start the services:
```bash
docker compose up
```

2. Access the services:
- Kafka: localhost:9092
- Zookeeper: localhost:2181
- Kafdrop UI: http://localhost:9001

## Simple Testing Steps

### 1. Verify Services
Check if all containers are running:
```bash
docker compose ps
```
You should see three containers running:
- distributed-pos-concept-zookeeper-1
- distributed-pos-concept-kafka-1
- distributed-pos-concept-kafdrop-1

### 2. Test Kafka (Command Line)

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

### 3. Test Kafdrop UI

1. Open http://localhost:9001 in your browser

2. Verify the setup:
   - Click "Brokers" to see Kafka broker status
   - Click "Topics" to see your test-topic
   - Click on test-topic to view messages
   - Click "Consumer Groups" to see active consumers

### 4. Clean Up

To stop all services:
```bash
docker compose down
```

## Troubleshooting

1. If ports are already in use:
   - Check if any other services are using ports 2181, 9092, or 9001
   - Modify the port mappings in docker-compose.yaml if needed

2. If services fail to start:
   - Check the logs: `docker compose logs`
   - Ensure Docker has enough resources allocated
   - Try removing all containers and volumes: `docker compose down -v`
