from fastapi import HTTPException
from sqlalchemy.orm import Session

from dao.item_dao import ItemDAO
from dao.item_order_dao import ItemOrderDao
from dao.order_dao import OrderDAO
from database.schema.item_order_schema import ItemOrderSchema
from models.item_order import ItemOrderCreate, ItemOrderResponse
from models.order_model import OrderUpdate
from service.order_service import OrderService


class ItemOrderService:
    def __init__(self, database: Session):
        self.item_order_dao = ItemOrderDao(database)
        self.item_dao = ItemDAO(database)
        self.order_dao = OrderDAO(database)
        self.order_service = OrderService(database)

    def create(self, item_order: ItemOrderCreate) -> ItemOrderResponse:
        item = self.item_dao.find_by_id(item_order.item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        order = self.order_dao.find_by_id(item_order.order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        new_item_order = ItemOrderSchema(
            quantity=item_order.quantity,
            order_id=item_order.order_id,
            item_id=item_order.item_id
        )

        item_order_created = None
        if not order.payment_status:
            item_order_created = self.item_order_dao.create(new_item_order)

        if not item_order_created:
            raise HTTPException(status_code=404, detail="Order is Closed for buying")

        amount = order.balance_amount + (item.price * item_order.quantity)
        updated_order = OrderUpdate(
            balance_amount=amount,
        )
        self.order_service.update(item_order.order_id, updated_order)

        return item_order_created

    def delete(self, item_order_id: int):
        item_order = self.item_order_dao.find_by_id(item_order_id)
        if not item_order:
            raise HTTPException(status_code=404, detail="Item not found in order")

        order = self.order_dao.find_by_id(item_order.order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.payment_status:
            raise HTTPException(status_code=404, detail="Order is Closed")

        if order.order_status == "Order Confirmed" or order.order_status == "Order Ready" or order.order_status == "Delivered Order":
            raise HTTPException(status_code=404, detail="Item can not be removed from the order")

        # _________________________________________________________
        item = self.item_dao.find_by_id(item_order.item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found in order")

        amount = order.balance_amount - (item.price * item_order.quantity)
        updated_order = OrderUpdate(
            balance_amount=amount,
        )
        self.order_service.update(item_order.order_id, updated_order)

        self.item_order_dao.delete(item_order)






