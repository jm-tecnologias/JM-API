from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SessionStatus(str, Enum):
    OPEN = "OPEN"
    CHECKOUT_REQUESTED = "CHECKOUT_REQUESTED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class OrderStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    PREPARING = "PREPARING"
    READY = "READY"
    SERVED = "SERVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class TableScanResponse(BaseModel):
    restaurant_id: int
    restaurant_name: str
    table_name: str
    table_token: str


class TableSessionCreate(BaseModel):
    table_token: str = Field(min_length=16, max_length=64)
    customer_name: str | None = Field(default=None, max_length=80)


class TableSessionOpened(BaseModel):
    session_id: str
    session_token: str
    status: SessionStatus
    restaurant_id: int
    table_name: str


class ClientOrderItemCreate(BaseModel):
    item_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=100)
    notes: str | None = Field(default=None, max_length=300)


class ClientOrderCreate(BaseModel):
    items: list[ClientOrderItemCreate] = Field(min_length=1, max_length=100)


class OrderItemResponse(BaseModel):
    id: int
    item_id: int
    item_name: str
    quantity: int
    unit_price: Decimal
    notes: str | None
    status: OrderStatus

    model_config = ConfigDict(from_attributes=True)


class DiningOrderResponse(BaseModel):
    id: int
    order_status: OrderStatus
    balance_amount: Decimal
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


class TableSessionSummary(BaseModel):
    session_id: str
    status: SessionStatus
    table_name: str
    total_amount: Decimal
    opened_at: datetime
    checkout_requested_at: datetime | None
    closed_at: datetime | None
    orders: list[DiningOrderResponse]


class StaffOrderStatusUpdate(BaseModel):
    status: OrderStatus


class PaymentConfirmation(BaseModel):
    method: str = Field(min_length=2, max_length=30)
    amount_received: Decimal = Field(gt=0, decimal_places=2)
    external_reference: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=255)


class PaymentRecordResponse(BaseModel):
    id: int
    method: str
    amount: Decimal
    external_reference: str | None
    confirmed_at: datetime

    model_config = ConfigDict(from_attributes=True)
