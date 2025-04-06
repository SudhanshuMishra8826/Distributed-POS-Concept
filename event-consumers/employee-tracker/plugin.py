import json
import os
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
from kafka import KafkaConsumer, KafkaProducer
import mysql.connector
from mysql.connector import Error
from pydantic import BaseModel
import redis
import pickle

# Load environment variables
load_dotenv()

class EmployeeSession(BaseModel):
    employee_id: str
    terminal_id: str
    login_time: datetime
    last_activity: datetime

class EmployeeTimeTracker:
    def __init__(self):
        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(","),
            group_id="employee_time_tracker",
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        # Initialize Kafka producer for publishing events
        self.producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(","),
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # Initialize Redis connection
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=0,
            decode_responses=False  # We need to store binary data for pickle
        )
        
        # Initialize MySQL connection
        self.db = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "pos_user"),
            password=os.getenv("MYSQL_PASSWORD", "password"),
            database=os.getenv("MYSQL_DATABASE", "pos_db"),
            port=int(os.getenv("MYSQL_PORT", "3306"))
        )
        
        # Create necessary database tables
        self._create_tables()
        
        # Subscribe to relevant topics
        self.consumer.subscribe(["pos_events"])

    def _get_active_session(self, employee_id: str) -> Optional[EmployeeSession]:
        """Get active session from Redis."""
        session_data = self.redis_client.get(f"employee_session:{employee_id}")
        if session_data:
            return pickle.loads(session_data)
        return None

    def _set_active_session(self, employee_id: str, session: EmployeeSession):
        """Store active session in Redis."""
        self.redis_client.set(
            f"employee_session:{employee_id}",
            pickle.dumps(session),
            ex=86400  # Expire after 24 hours
        )

    def _delete_active_session(self, employee_id: str):
        """Delete active session from Redis."""
        self.redis_client.delete(f"employee_session:{employee_id}")

    def _create_tables(self):
        """Create necessary database tables if they don't exist."""
        cursor = self.db.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employee_sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    employee_id VARCHAR(255) NOT NULL,
                    terminal_id VARCHAR(255) NOT NULL,
                    login_time TIMESTAMP NOT NULL,
                    logout_time TIMESTAMP NULL,
                    duration INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_employee (employee_id),
                    INDEX idx_terminal (terminal_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            self.db.commit()
        except Error as e:
            print(f"Error creating tables: {e}")
        finally:
            cursor.close()

    def _handle_employee_login(self, event: dict):
        """Handle employee login event."""
        employee_id = event["employee_id"]
        terminal_id = event["terminal_id"]
        
        # Check if employee is already logged in at another terminal
        existing_session = self._get_active_session(employee_id)
        if existing_session and existing_session.terminal_id != terminal_id:
            # Auto-logout from previous terminal
            self._handle_employee_logout({
                "employee_id": employee_id,
                "terminal_id": existing_session.terminal_id
            })
        
        # Create new session
        session = EmployeeSession(
            employee_id=employee_id,
            terminal_id=terminal_id,
            login_time=datetime.fromisoformat(event["timestamp"]),
            last_activity=datetime.fromisoformat(event["timestamp"])
        )
        
        # Store in Redis
        self._set_active_session(employee_id, session)
        
        # Log to database
        cursor = self.db.cursor()
        try:
            cursor.execute("""
                INSERT INTO employee_sessions (employee_id, terminal_id, login_time)
                VALUES (%s, %s, %s)
            """, (employee_id, terminal_id, session.login_time))
            self.db.commit()
        except Error as e:
            print(f"Error logging employee login: {e}")
        finally:
            cursor.close()

    def _handle_employee_logout(self, event: dict):
        """Handle employee logout event."""
        employee_id = event["employee_id"]
        terminal_id = event["terminal_id"]
        
        # Get session from Redis
        session = self._get_active_session(employee_id)
        if not session:
            return
        
        # Verify terminal_id matches
        if session.terminal_id != terminal_id:
            return
        
        # Calculate duration
        logout_time = datetime.fromisoformat(event["timestamp"])
        duration = int((logout_time - session.login_time).total_seconds())
        
        # Update database
        cursor = self.db.cursor()
        try:
            cursor.execute("""
                UPDATE employee_sessions
                SET logout_time = %s, duration = %s
                WHERE employee_id = %s AND terminal_id = %s
                AND logout_time IS NULL
            """, (logout_time, duration, employee_id, terminal_id))
            self.db.commit()
        except Error as e:
            print(f"Error logging employee logout: {e}")
        finally:
            cursor.close()
        
        # Clean up Redis
        self._delete_active_session(employee_id)

    def _handle_item_addition(self, event: dict):
        """Update last activity time for employee."""
        basket_id = event["basket_id"]
        
        # Get employee_id from basket_id (this would typically come from a basket service)
        # For now, we'll just update all active sessions
        # Note: In a production environment, you'd want to get the employee_id from the basket service
        for key in self.redis_client.scan_iter("employee_session:*"):
            session = self._get_active_session(key.decode('utf-8').split(':')[1])
            if session:
                session.last_activity = datetime.fromisoformat(event["timestamp"])
                self._set_active_session(session.employee_id, session)

    def process_event(self, event: dict):
        """Process incoming events."""
        event_type = event["event_type"]
        
        if event_type == "employee_login":
            self._handle_employee_login(event)
        elif event_type == "employee_logout":
            self._handle_employee_logout(event)
        elif event_type == "item_added":
            self._handle_item_addition(event)

    def run(self):
        """Main event processing loop."""
        print("Starting Employee Time Tracker plugin...")
        try:
            for message in self.consumer:
                try:
                    event = message.value
                    self.process_event(event)
                except Exception as e:
                    print(f"Error processing message: {e}")
                    continue
        except KeyboardInterrupt:
            print("\nShutting down Employee Time Tracker plugin...")
        finally:
            self.consumer.close()
            self.producer.close()
            self.db.close()
            self.redis_client.close()

if __name__ == "__main__":
    tracker = EmployeeTimeTracker()
    tracker.run() 