from sqlalchemy import select
from sqlalchemy.orm import Session

from database.schema.menu_schema import MenuSchema


class MenuDao:
    def __init__(self, database: Session):
        self.database = database

    def create(self, menu: MenuSchema) -> MenuSchema:
        self.database.add(menu)
        self.database.commit()
        self.database.refresh(menu)
        return menu

    def find_by_id(self, menu_id: int) -> MenuSchema | None:
        st = select(MenuSchema).where(MenuSchema.id == menu_id)
        return self.database.scalar(st)

    def find_by_name(self, name: str) -> MenuSchema | None:
        st = select(MenuSchema).where(MenuSchema.name == name)
        return self.database.scalar(st)

    def find_all_menus(self, skip: int = 0, limit:int = 100) -> list[MenuSchema]:
        st = select(MenuSchema).offset(skip).limit(limit).order_by(MenuSchema.id)
        return self.database.scalars(st).all()

    def find_menus_by_restaurant_id(self, res_id: int, skip: int=0, limit:int=100) -> list[MenuSchema]:
        st = select(MenuSchema).offset(skip).limit(limit).where(MenuSchema.restaurant_id==res_id).order_by(MenuSchema.id)
        return self.database.scalars(st).all()

    def update(self, menu: MenuSchema) -> MenuSchema:
        self.database.add(menu)
        self.database.commit()
        self.database.refresh(menu)
        return menu

    def delete(self, menu: MenuSchema) -> None:
        self.database.delete(menu)
        self.database.commit()

    def rollback(self) -> None:
        self.database.rollback()