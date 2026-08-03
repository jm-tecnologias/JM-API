
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.schema.menu_schema import ItemSchema


class ItemDAO:
    def __init__(self, database:Session):
        self.database = database

    def create(self, item: ItemSchema) -> ItemSchema:
        self.database.add(item)
        self.database.commit()
        self.database.refresh(item)
        return item

    def update(self, item: ItemSchema) -> ItemSchema:
        self.database.add(item)
        self.database.commit()
        self.database.refresh(item)
        return item

    def find_by_id(self, item_id: int) -> ItemSchema | None:
        st = select(ItemSchema).where(ItemSchema.id == item_id)
        return self.database.scalar(st)

    def find_by_name(self, name: str) -> ItemSchema:
        st = select(ItemSchema).where(ItemSchema.name == name)
        return self.database.scalar(st)

    def find_items_by_menu_id(self, menu_id: int, skip: int = 0, limit:int = 100) -> list[ItemSchema]:
        st = select(ItemSchema).offset(skip).limit(limit).where(ItemSchema.menu_id == menu_id).order_by(ItemSchema.name)
        return self.database.scalars(st).all()

    def find_all_items(self, skip:int = 0, limit:int = 100) -> list[ItemSchema]:
        st = select(ItemSchema).offset(skip).limit(limit).order_by(ItemSchema.name)
        return self.database.scalars(st).all()