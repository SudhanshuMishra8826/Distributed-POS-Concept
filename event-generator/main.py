import os
import time
from dotenv import load_dotenv
from generator import EventGenerator


def main():
    # Load environment variables
    load_dotenv()

    # Get configuration from environment
    kafka_bootstrap_servers = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "localhost:9092"
    ).split(",")
    
    kafka_topic = os.getenv("KAFKA_TOPIC", "pos_events")
    delay_between_sequences = float(os.getenv("DELAY_BETWEEN_SEQUENCES", "5.0"))
    
    # Initialize event generator
    generator = EventGenerator(kafka_bootstrap_servers)
    
    print(f"Starting event generator...")
    print(f"Kafka servers: {kafka_bootstrap_servers}")
    print(f"Topic: {kafka_topic}")
    print(f"Delay between sequences: {delay_between_sequences} seconds")
    
    try:
        while True:
            print("\nGenerating new transaction sequence...")
            generator.generate_and_publish_sequence(kafka_topic)
            print("Transaction sequence completed successfully")
            print(f"Waiting {delay_between_sequences} seconds before next "
                  f"sequence...")
            time.sleep(delay_between_sequences)
            
    except KeyboardInterrupt:
        print("\nShutting down event generator...")
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main() 