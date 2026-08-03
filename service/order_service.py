from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dao.order_dao import OrderDAO
from dao.table_dao import TableDAO
from dao.user_dao import UserDao
from database.schema.order_schema import OrderSchema
from models.order_model import OrderCreate, OrderResponse, OrderUpdate


class OrderService:
    def __init__(self, database: Session):
        self.order_dao = OrderDAO(database)
        self.user_dao = UserDao(database)
        self.table_dao = TableDAO(database)

    def create(self, order: OrderCreate) -> OrderResponse:
        user =  self.user_dao.find_by_id(order.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        table = self.table_dao.find_by_id(order.table_id)
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")

        new_order = OrderSchema(
            order_status=order.order_status,
            payment_status=order.payment_status,
            balance_amount=order.balance_amount,
            user_id=order.user_id,
            table_id=order.table_id
        )
        return self.order_dao.create(new_order)

    def update(self,order_id:int, order_data: OrderUpdate) -> OrderSchema:
        order = self.order_dao.find_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        print("DATA: ",order_data.balance_amount)
        updated_order = order_data.model_dump(exclude_unset=True)

        for field, value in updated_order.items():
            setattr(order, field, value)
        try:
            return self.order_dao.create(order)
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail="Was Order already exists")