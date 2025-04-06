import json
import time
import uuid
from datetime import datetime
from typing import List, Dict
from faker import Faker
from kafka import KafkaProducer
from models import (
    EmployeeEvent, CustomerEvent, ItemEvent, BasketEvent,
    SubtotalEvent, PaymentEvent, LogoutEvent, POSEvent
)

fake = Faker()

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class EventGenerator:
    def __init__(self, bootstrap_servers: List[str]):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(
                v, cls=DateTimeEncoder).encode('utf-8')
        )
        self.employees: Dict[str, str] = {}  # employee_id -> terminal_id
        self.baskets: Dict[str, str] = {}    # basket_id -> employee_id
        self.items = [
            {"id": "001", "name": "Milk", "price": 3.99},
            {"id": "002", "name": "Bread", "price": 2.49},
            {"id": "003", "name": "Eggs", "price": 4.99},
            {"id": "004", "name": "Beer", "price": 8.99},
            {"id": "005", "name": "Wine", "price": 15.99},
        ]

    def generate_employee_login(self) -> EmployeeEvent:
        employee_id = str(uuid.uuid4())
        terminal_id = str(uuid.uuid4())
        self.employees[employee_id] = terminal_id
        return EmployeeEvent(
            employee_id=employee_id,
            terminal_id=terminal_id
        )

    def generate_basket_start(self) -> BasketEvent:
        if not self.employees:
            raise ValueError("No employees logged in")
        
        employee_id = list(self.employees.keys())[0]
        basket_id = str(uuid.uuid4())
        self.baskets[basket_id] = employee_id
        return BasketEvent(
            basket_id=basket_id,
            employee_id=employee_id
        )

    def generate_customer_identification(self) -> CustomerEvent:
        if not self.baskets:
            raise ValueError("No active baskets")
        
        basket_id = list(self.baskets.keys())[0]
        return CustomerEvent(
            customer_id=str(uuid.uuid4()),
            basket_id=basket_id
        )

    def generate_item_addition(self) -> ItemEvent:
        if not self.baskets:
            raise ValueError("No active baskets")
        
        basket_id = list(self.baskets.keys())[0]
        item = fake.random_element(self.items)
        return ItemEvent(
            item_id=item["id"],
            basket_id=basket_id,
            quantity=fake.random_int(min=1, max=5),
            price=item["price"]
        )

    def generate_subtotal(self) -> SubtotalEvent:
        if not self.baskets:
            raise ValueError("No active baskets")
        basket_id = list(self.baskets.keys())[0]
        # Generate numbers between 10 and 109
        subtotal = float(fake.random_number(digits=2)) + 10.0
        tax = subtotal * 0.1
        return SubtotalEvent(
            basket_id=basket_id,
            subtotal=subtotal,
            tax=tax
        )

    def generate_payment(self) -> PaymentEvent:
        if not self.baskets:
            raise ValueError("No active baskets")
        
        basket_id = list(self.baskets.keys())[0]
        # Generate amount between 10 and 109
        amount = float(fake.random_number(digits=2)) + 10.0
        payment_method = fake.random_element(
            ["credit_card", "debit_card", "cash"]
        )
        return PaymentEvent(
            basket_id=basket_id,
            amount=amount,
            payment_method=payment_method
        )

    def generate_employee_logout(self) -> LogoutEvent:
        if not self.employees:
            raise ValueError("No employees logged in")
        
        employee_id = list(self.employees.keys())[0]
        terminal_id = self.employees[employee_id]
        del self.employees[employee_id]
        return LogoutEvent(
            employee_id=employee_id,
            terminal_id=terminal_id
        )

    def publish_event(self, event: POSEvent, topic: str):
        self.producer.send(topic, value=event.dict())
        self.producer.flush()

    def generate_and_publish_sequence(self, topic: str, delay: float = 1.0):
        """
        Generate and publish a sequence of events
        simulating a complete POS transaction.
        """
        try:
            # Employee login
            login_event = self.generate_employee_login()
            self.publish_event(login_event, topic)
            time.sleep(delay)

            # Start basket
            basket_event = self.generate_basket_start()
            self.publish_event(basket_event, topic)
            time.sleep(delay)

            # Customer identification
            customer_event = self.generate_customer_identification()
            self.publish_event(customer_event, topic)
            time.sleep(delay)

            # Add items (2-4 items)
            for _ in range(fake.random_int(min=2, max=4)):
                item_event = self.generate_item_addition()
                self.publish_event(item_event, topic)
                time.sleep(delay)

            # Calculate subtotal
            subtotal_event = self.generate_subtotal()
            self.publish_event(subtotal_event, topic)
            time.sleep(delay)

            # Payment
            payment_event = self.generate_payment()
            self.publish_event(payment_event, topic)
            time.sleep(delay)

            # Employee logout
            logout_event = self.generate_employee_logout()
            self.publish_event(logout_event, topic)

        except Exception as e:
            print(f"Error generating sequence: {e}")
            raise 