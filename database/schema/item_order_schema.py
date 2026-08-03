from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, String
from sqlalchemy.orm import relationship

from database.base import Base


class ItemOrderSchema(Base):
    __tablename__ = "item_order"
    id = Column("id", Integer, primary_key=True)
    order_id = Column("order_id", Integer, ForeignKey("order.id"), nullable=False)
    item_id = Column("item_id", Integer, ForeignKey("item.id"), nullable=False)
    quantity = Column("quantity", Integer, default=1, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False, default=0)
    item_name = Column(String, nullable=False, default="")
    notes = Column(String, nullable=True)
    status = Column(String, nullable=False, default="SUBMITTED")
    created_at = Column("created_at", DateTime, nullable=False, default=datetime.now)
    order = relationship(
        "OrderSchema",
        back_populates="items",
    )

    def __init__(self, order_id:int, item_id:int, quantity:int = 1, unit_price=0, item_name="", notes=None, status="SUBMITTED"):
        self.order_id = order_id
        self.item_id = item_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.item_name = item_name
        self.notes = notes
        self.status = status
