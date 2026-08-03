from sqlalchemy import select
from sqlalchemy.orm import Session

from database.schema.order_schema import OrderSchema
from models.order_model import OrderModel


class OrderDAO:

    def __init__(self, database: Session):
        self.database = database

    def create(self, order: OrderModel) -> OrderSchema:
        self.database.add(order)
        self.database.commit()
        self.database.refresh(order)
        return order

    def find_by_id(self, order_id: int) -> OrderSchema | None:
        st = select(OrderSchema).where(OrderSchema.id == order_id)
        return self.database.scalar(st)

    def delete(self, order: OrderSchema) -> None:
        self.database.delete(order)
        self.database.commit()

    def rollback(self) -> None:
        self.database.rollback()
