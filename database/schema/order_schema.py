from datetime import datetime

from sqlalchemy import Column, Integer, Boolean, DateTime, String, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database.base import Base


class OrderSchema(Base):
    __tablename__ = "order"
    __table_args__ = (
        UniqueConstraint("table_session_id", "request_key", name="uq_session_order_request"),
    )


    id = Column("id", Integer, primary_key=True, autoincrement=True)
    order_status = Column("order_status", String, nullable=False, default="SUBMITTED")
    payment_status = Column("payment_status", Boolean, nullable=False, default=False)
    balance_amount = Column("balance_amount", Numeric(12, 2), nullable=False, default=0)
    user_id = Column("user_id", Integer, ForeignKey("user.id"), nullable=True)
    table_id = Column("table_id", Integer, ForeignKey("table.id"), nullable=True)
    table_session_id = Column(Integer, ForeignKey("table_session.id"), nullable=True, index=True)
    request_key = Column(String(80), nullable=True)
    created_at = Column("created_at", DateTime, nullable=False, default=datetime.now)
    updated_at = Column("updated_at", DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    items = relationship(
        "ItemOrderSchema",
        back_populates="order",
        order_by="ItemOrderSchema.id",
        cascade="all, delete-orphan",
    )
    table_session = relationship("TableSessionSchema", back_populates="orders")
    def __init__(self, user_id:int, table_id:int, order_status="Draft",payment_status=False,balance_amount=0.0):
        self.order_status = order_status
        self.payment_status = payment_status
        self.balance_amount = balance_amount
        self.user_id = user_id
        self.table_id = table_id
