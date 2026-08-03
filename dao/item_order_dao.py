from sqlalchemy import select
from sqlalchemy.orm import Session

from database.schema.item_order_schema import ItemOrderSchema


class ItemOrderDao:
    def __init__(self, database: Session):
        self.database = database

    def create(self, item_order: ItemOrderSchema) -> ItemOrderSchema:
        self.database.add(item_order)
        self.database.commit()
        self.database.refresh(item_order)
        return item_order

    def find_by_id(self, item_order_id: int) -> ItemOrderSchema:
        st = select(ItemOrderSchema).where(ItemOrderSchema.id == item_order_id)
        return self.database.scalar(st)

    def delete(self, item_order: ItemOrderSchema):
        self.database.delete(item_order)
        self.database.commit()
        # self.database.refresh(item_order)


    def rollback(self):
        self.database.rollback()
