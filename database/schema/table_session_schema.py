import secrets
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import relationship

from database.base import Base


class TableSessionSchema(Base):
    __tablename__ = "table_session"
    __table_args__ = (
        UniqueConstraint("table_id", "active_key", name="uq_active_table_session"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    public_id = Column(String(64), nullable=False, unique=True, index=True, default=lambda: secrets.token_urlsafe(24))
    restaurant_id = Column(Integer, ForeignKey("restaurant.id"), nullable=False, index=True)
    table_id = Column(Integer, ForeignKey("table.id"), nullable=False, index=True)
    opened_by_user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    customer_name = Column(String(80), nullable=True)
    status = Column(String(32), nullable=False, default="OPEN", index=True)
    active_key = Column(String(16), nullable=True, default="ACTIVE")
    total_amount = Column(Numeric(12, 2), nullable=False, default=0)
    opened_at = Column(DateTime, nullable=False, default=datetime.now)
    checkout_requested_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    table = relationship("TableSchema", back_populates="sessions")
    orders = relationship("OrderSchema", back_populates="table_session", order_by="OrderSchema.created_at")
    payments = relationship("PaymentRecordSchema", back_populates="table_session")


class PaymentRecordSchema(Base):
    __tablename__ = "payment_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_session_id = Column(Integer, ForeignKey("table_session.id"), nullable=False, index=True)
    method = Column(String(30), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    external_reference = Column(String(100), nullable=True)
    notes = Column(String(255), nullable=True)
    confirmed_by_user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    confirmed_at = Column(DateTime, nullable=False, default=datetime.now)

    table_session = relationship("TableSessionSchema", back_populates="payments")
