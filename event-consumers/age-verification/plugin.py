#!/usr/bin/env python3
"""
Age Verification Plugin

This plugin monitors item added events from the POS system and determines
if age verification is required when certain items are purchased.
"""

import os
import json
import uuid
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from kafka import KafkaConsumer, KafkaProducer
import redis

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('age-verification-plugin')

# Age-restricted item IDs and their minimum age requirements
AGE_RESTRICTED_ITEM_IDS = {
    '004': 21,  # Beer
    '005': 21   # Wine
}

class AgeVerificationPlugin:
    def __init__(self):
        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            'pos_events',
            bootstrap_servers=os.getenv('KAFKA_BROKER', 'localhost:9092').split(','),
            group_id='age-verification-group',
            auto_offset_reset='latest',
            enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        # Initialize Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=os.getenv('KAFKA_BROKER', 'localhost:9092').split(','),
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # Initialize Redis client
        self.redis = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', ''),
            decode_responses=True
        )
        
        # Running flag for graceful shutdown
        self.running = True
        
        # Set up signal handlers
        import signal
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
    
    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Shutting down...")
        self.running = False
    
    async def start(self):
        """Start the plugin"""
        try:
            logger.info("Age Verification Plugin started")
            
            # Start consuming messages
            await self.consume_messages()
        except Exception as e:
            logger.error(f"Error starting plugin: {str(e)}")
            await self.close()
    
    async def consume_messages(self):
        """Consume messages from Kafka"""
        try:
            for message in self.consumer:
                if not self.running:
                    break
                
                try:
                    event = message.value
                    await self.process_event(event)
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    logger.error(f"Message that caused error: {json.dumps(event)}")
        except Exception as e:
            logger.error(f"Error in consumer loop: {str(e)}")
            if self.running:
                await asyncio.sleep(5)
                await self.consume_messages()
    
    async def process_event(self, event):
        """Process an event"""
        try:
            # Log every valid event
            logger.info(f"Received event: {json.dumps(event)}")
            
            event_type = event.get('event_type')
            basket_id = event.get('basket_id', 'unknown')
            
            # Check if it's an item_added event
            if event_type == 'item_added':
                logger.info(f"Processing item_added event for basket {basket_id}")
                
                # Check if age verification is required
                age_verification_required = await self.check_age_verification_required(event)
                
                if age_verification_required.get('required', False):
                    logger.info(f"Age verification required for basket {basket_id}")
                    await self.create_age_verification_required_event(event, age_verification_required)
                else:
                    logger.info(f"No age verification required for basket {basket_id}")
            else:
                logger.info(f"Skipping non-item event: {event_type}")
        except Exception as e:
            logger.error(f"Error processing event: {str(e)}")
            logger.error(f"Event that caused error: {json.dumps(event)}")
    
    async def check_age_verification_required(self, event):
        """Check if age verification is required for the item"""
        try:
            item_id = event.get('item_id', '')
            
            # Check if the item ID is age-restricted
            print(f"Checking age verification for item ID: {item_id} {AGE_RESTRICTED_ITEM_IDS}")
            if item_id in AGE_RESTRICTED_ITEM_IDS:
                min_age = AGE_RESTRICTED_ITEM_IDS[item_id]
                return {
                    'required': True,
                    'min_age': min_age,
                    'item_id': item_id,
                }
            
            return {'required': False}
        except Exception as e:
            logger.error(f"Error checking age verification: {str(e)}")
            return {'required': False}
    
    async def create_age_verification_required_event(self, event, verification_info):
        """Create an age verification required event"""
        try:
            basket_id = event.get('basket_id', 'unknown')
            customer_id = event.get('customer_id', 'anonymous')
            
            age_verification_event = {
                'event_type': 'age_verification_required',
                'verification_id': str(uuid.uuid4()),
                'customer_id': customer_id,
                'basket_id': basket_id,
                'min_age': verification_info.get('min_age'),
                'item_id': verification_info.get('item_id'),
                'item_name': verification_info.get('item_name'),
                'timestamp': datetime.now().isoformat(),
                'original_event': {
                    'event_type': event.get('event_type'),
                    'timestamp': event.get('timestamp')
                }
            }
            
            # Send the event to Kafka
            self.producer.send(
                'pos_events',
                key=age_verification_event['verification_id'].encode('utf-8'),
                value=age_verification_event
            )
            
            logger.info(f"Age verification required event created for basket {basket_id}")
        except Exception as e:
            logger.error(f"Error creating age verification event: {str(e)}")
    
    async def close(self):
        """Close connections"""
        try:
            self.consumer.close()
            self.producer.close()
            self.redis.close()
            logger.info("Connections closed")
        except Exception as e:
            logger.error(f"Error closing connections: {str(e)}")

# Start the plugin
if __name__ == "__main__":
    plugin = AgeVerificationPlugin()
    asyncio.run(plugin.start()) 