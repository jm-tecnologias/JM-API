from datetime import datetime

from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class ItemOrderModel(BaseModel):
    quantity: int = Field(gt=0)

class ItemOrderCreate(ItemOrderModel):
    order_id: int = Field(gt=0)
    item_id: int = Field(gt=0)

class ItemOrderResponse(BaseModel):
    id: int
    order_id: int
    item_id: int
    quantity: int
    unit_price: Decimal
    item_name: str
    notes: str | None = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
