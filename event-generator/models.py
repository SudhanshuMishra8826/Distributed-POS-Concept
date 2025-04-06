from datetime import datetime
from typing import Union
from pydantic import BaseModel, Field


class EmployeeEvent(BaseModel):
    event_type: str = "employee_login"
    employee_id: str
    terminal_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CustomerEvent(BaseModel):
    event_type: str = "customer_identified"
    customer_id: str
    basket_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ItemEvent(BaseModel):
    event_type: str = "item_added"
    item_id: str
    basket_id: str
    quantity: int
    price: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BasketEvent(BaseModel):
    event_type: str = "basket_started"
    basket_id: str
    employee_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SubtotalEvent(BaseModel):
    event_type: str = "subtotal_calculated"
    basket_id: str
    subtotal: float
    tax: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaymentEvent(BaseModel):
    event_type: str = "payment_completed"
    basket_id: str
    amount: float
    payment_method: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class LogoutEvent(BaseModel):
    event_type: str = "employee_logout"
    employee_id: str
    terminal_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Union type for all possible events
POSEvent = Union[
    EmployeeEvent,
    CustomerEvent,
    ItemEvent,
    BasketEvent,
    SubtotalEvent,
    PaymentEvent,
    LogoutEvent
]