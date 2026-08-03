from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from dao import item_dao
from dao.item_dao import ItemDAO
from dao.menu_dao import MenuDao
from database.schema.menu_schema import ItemSchema
from models.menu_model import ItemCreate, ItemResponse, ItemUpdate


class ItemService:
    def __init__(self, db: Session):
        self.item_dao = ItemDAO(db)
        self.menu_dao = MenuDao(db)

    def create_item(self, item: ItemCreate) -> ItemResponse:
        menu = self.menu_dao.find_by_id(item.menu_id)
        if not menu:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")

        existing_item = self.item_dao.find_by_name(item.name)
        if existing_item:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item already exists")

        new_item = ItemSchema(
            name=item.name,
            price=item.price,
            menu_id=item.menu_id,
            description=item.description,
            profile_pic_url=item.profile_pic_url
        )
        return self.item_dao.create(new_item)
    
    def update(self, item_id: int, item_data: ItemUpdate) -> ItemSchema:
        item = self.item_dao.find_by_id(item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

        updated_item = item_data.model_dump(exclude_unset=True)

        if "name" in updated_item:
            name = updated_item["name"]
            if name == item.name:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item already exists")

        if "price" in updated_item:
            price = updated_item["price"]
            if price == item.price:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item price is the same")

        for field, value in updated_item.items():
            setattr(item, field, value)

        try:
            return self.item_dao.update(item)
        except HTTPException:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Was not able to update item data")

    def find_all_menu_items(self, menu_id: int, skip: int = 0, limit: int = 100) -> list[ItemResponse]:
        return self.item_dao.find_items_by_menu_id(menu_id, skip, limit)

    def find_all_items(self,skip: int = 0, limit: int = 100) -> list[ItemResponse]:
        return self.item_dao.find_all_items(skip, limit)
