import json
import logging
from typing import Dict, Any, Callable
from kafka import KafkaConsumer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)

class JobRequestConsumer:
    """Kafka consumer for job requests"""
    
    def __init__(self, brokers: list, topic: str, group_id: str = "job-finder-group"):
        self.brokers = brokers
        self.topic = topic
        self.group_id = group_id
        self.consumer = None
        self.message_handler: Callable[[Dict[str, Any]], None] = None
        
    def connect(self):
        """Connect to Kafka"""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.brokers,
                group_id=self.group_id,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                key_deserializer=lambda x: x.decode('utf-8') if x else None
            )
            logger.info(f"Connected to Kafka topic: {self.topic}")
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
            
    def set_message_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Set the message handler function"""
        self.message_handler = handler
        
    def start_consuming(self):
        """Start consuming messages"""
        if not self.consumer:
            self.connect()
            
        if not self.message_handler:
            raise ValueError("Message handler not set")
            
        logger.info(f"Starting to consume messages from topic: {self.topic}")
        
        try:
            for message in self.consumer:
                try:
                    logger.info(f"Received message: {message.value}")
                    self.message_handler(message.value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
        finally:
            self.stop()
            
    def stop(self):
        """Stop the consumer"""
        if self.consumer:
            self.consumer.close()
            logger.info("Consumer stopped") 