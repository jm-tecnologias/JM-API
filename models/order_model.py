from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from models.item_order import ItemOrderModel


class OrderModel(BaseModel):
    order_status: str = Field(default="Draft")
    payment_status: bool = Field(default=False)
    balance_amount: float = Field(default=0.0)


class OrderCreate(OrderModel):
    user_id: int = Field(gt=0)
    table_id: int = Field(gt=0)

class OrderUpdate(BaseModel):
    order_status: str | None = None
    payment_status: bool| None = None
    balance_amount: float | None = None

class OrderResponse(OrderModel):
    id: int
    created_at: datetime
    updated_at: datetime
    items: list[ItemOrderModel] = Field(default_factory=list)

    model_config = ConfigDict(
        from_attributes=True,
    )
