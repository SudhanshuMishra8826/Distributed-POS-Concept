#!/usr/bin/env python3
import os
import json
import time
import signal
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from kafka import KafkaConsumer, KafkaProducer
from redis import Redis
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class CustomerData:
    """Customer information data structure"""
    def __init__(self, customer_id: str, first_name: str = "", last_name: str = "", 
                 email: str = "", phone_number: str = "", membership_tier: str = "Standard",
                 points: int = 0, last_visit: Optional[datetime] = None):
        self.customer_id = customer_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.membership_tier = membership_tier
        self.points = points
        self.last_visit = last_visit or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "customer_id": self.customer_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "membership_tier": self.membership_tier,
            "points": self.points,
            "last_visit": self.last_visit.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomerData':
        """Create CustomerData from dictionary"""
        return cls(
            customer_id=data.get("customer_id", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            email=data.get("email", ""),
            phone_number=data.get("phone_number", ""),
            membership_tier=data.get("membership_tier", "Standard"),
            points=data.get("points", 0),
            last_visit=datetime.fromisoformat(data["last_visit"]) if "last_visit" in data else None
        )

# Default customer data for fallback
DEFAULT_CUSTOMER_DATA = CustomerData(
    customer_id="ANONYMOUS",
    first_name="Guest",
    last_name="Customer",
    email="",
    phone_number="",
    membership_tier="Standard",
    points=0
)

class CustomerLookupPlugin:
    """Plugin for looking up customer data and caching it"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            bootstrap_servers=os.getenv("KAFKA_BROKER", "localhost:9092").split(","),
            group_id=f"customer-lookup-{uuid.uuid4()}",
            auto_offset_reset="latest",
            enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        # Subscribe to the topic
        self.consumer.subscribe(["pos_events"])
        
        # Initialize Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BROKER", "localhost:9092").split(","),
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # Initialize Redis client
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_password = os.getenv("REDIS_PASSWORD", "")
        
        self.redis_client = Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True
        )
        
        # Flag for graceful shutdown
        self.running = True
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
    
    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Shutting down...")
        self.running = False
    
    def get_customer_from_cache(self, customer_id: str) -> Optional[CustomerData]:
        """Get customer data from Redis cache"""
        try:
            data = self.redis_client.get(f"customer:{customer_id}")
            if data:
                return CustomerData.from_dict(json.loads(data))
            return None
        except Exception as e:
            logger.error(f"Error getting customer from cache: {e}")
            return None
    
    def cache_customer_data(self, customer_data: CustomerData) -> None:
        """Cache customer data in Redis"""
        try:
            # Cache for 1 hour
            self.redis_client.setex(
                f"customer:{customer_data.customer_id}",
                3600,  # 1 hour in seconds
                json.dumps(customer_data.to_dict())
            )
        except Exception as e:
            logger.error(f"Error caching customer data: {e}")
    
    def fetch_customer_from_remote(self, customer_id: str) -> CustomerData:
        """Fetch customer data from remote system (simulated)"""
        # In a real implementation, this would make an HTTP request to a customer service
        # For now, we'll simulate with mock data
        return CustomerData(
            customer_id=customer_id,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="+1234567890",
            membership_tier="Gold",
            points=1000
        )
    
    def ensure_customer_data_fields(self, data: CustomerData, customer_id: str) -> CustomerData:
        """Ensure all required fields are present in customer data"""
        if data is None:
            data = DEFAULT_CUSTOMER_DATA
        
        # Ensure CustomerID is set
        if not data.customer_id:
            data.customer_id = customer_id
        
        # Ensure FirstName is set
        if not data.first_name:
            data.first_name = "Guest"
        
        # Ensure LastName is set
        if not data.last_name:
            data.last_name = "Customer"
        
        # Ensure MembershipTier is set
        if not data.membership_tier:
            data.membership_tier = "Standard"
        
        # Ensure LastVisit is set
        if data.last_visit is None:
            data.last_visit = datetime.now()
        
        return data
    
    def handle_customer_identified(self, customer_id: str, basket_id: str) -> None:
        """Handle customer identification event"""
        customer_data = None
        
        # Try to get customer data from Redis cache first
        customer_data = self.get_customer_from_cache(customer_id)
        
        if customer_data is None:
            # If not in cache, fetch from remote system
            try:
                customer_data = self.fetch_customer_from_remote(customer_id)
                # Cache the successfully fetched customer data
                self.cache_customer_data(customer_data)
            except Exception as e:
                logger.error(f"Error fetching customer data: {e}")
                # Use default customer data
                customer_data = DEFAULT_CUSTOMER_DATA
                customer_data.customer_id = customer_id  # Preserve the original customer ID
        
        # Ensure all required fields are present
        customer_data = self.ensure_customer_data_fields(customer_data, customer_id)
        
        # Publish customer data event
        self.publish_customer_data(customer_data, basket_id)
    
    def publish_customer_data(self, customer_data: CustomerData, basket_id: str) -> None:
        """Publish customer data to Kafka"""
        event = {
            "event_type": "customer_data",
            "customer_id": customer_data.customer_id,
            "basket_id": basket_id,
            "customer_data": customer_data.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            self.producer.send("pos_events", value=event, key=customer_data.customer_id.encode('utf-8'))
            self.producer.flush()
            logger.info(f"Published customer data for customer {customer_data.customer_id} in basket {basket_id}")
        except Exception as e:
            logger.error(f"Error publishing customer data: {e}")
    
    def start(self) -> None:
        """Start consuming messages"""
        logger.info("Customer Lookup Plugin started")
        
        try:
            while self.running:
                # Poll for messages with a timeout
                message_batch = self.consumer.poll(timeout_ms=1000)
                
                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        try:
                            event = message.value
                            
                            # Check if this is a customer identifier event
                            if event.get("event_type") == "customer_identified":
                                customer_id = event.get("customer_id", "")
                                basket_id = event.get("basket_id", "")
                                
                                if customer_id and basket_id:
                                    self.handle_customer_identified(customer_id, basket_id)
                                else:
                                    logger.warning("Received customer_identified event with missing customer_id or basket_id")
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
        except Exception as e:
            logger.error(f"Error in consumer loop: {e}")
        finally:
            self.close()
    
    def close(self) -> None:
        """Close connections"""
        try:
            self.consumer.close()
            self.producer.close()
            self.redis_client.close()
        except Exception as e:
            logger.error(f"Error closing connections: {e}")

def main():
    """Main entry point"""
    plugin = CustomerLookupPlugin()
    plugin.start()

if __name__ == "__main__":
    main() 