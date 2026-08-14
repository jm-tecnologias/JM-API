from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dao.menu_dao import MenuDao
from dao.restaurante_dao import RestauranteDao
from database.schema.menu_schema import MenuSchema
from models.menu_model import MenuCreate, MenuResponse, MenuUpdate


class MenuService:
    def __init__(self, database: Session):
        self.restaurant_dao = RestauranteDao(database)
        self.menu_dao = MenuDao(database)

    def create(self, menu: MenuCreate) -> MenuResponse:
        restaurant = self.restaurant_dao.find_by_id(menu.restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

        new_menu = MenuSchema(
            name=menu.name,
            restaurant_id=menu.restaurant_id,
            description=menu.description,
            profile_pic_url=menu.profile_pic_url
        )
        return self.menu_dao.create(new_menu)

    def update(self, menu_id: int, menu_data: MenuUpdate) -> MenuSchema:
        menu = self.menu_dao.find_by_id(menu_id)
        if not menu:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")

        updated_menu = menu_data.model_dump(exclude_unset=True)

        if "name" in updated_menu:
            name = updated_menu["name"]
            if name == menu.name:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu name already exists")

        for field, value in updated_menu.items():
            setattr(menu, field, value)
        try:
            return self.menu_dao.update(menu)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Was not possible to update this menu data")

    def find_all_restaurant_menus(self, restaurant_id: int, skip, limit) -> list[MenuResponse]:
        return self.menu_dao.find_menus_by_restaurant_id(restaurant_id, skip, limit)

    def find_all(self, skip, limit) -> list[MenuResponse]:
        return self.menu_dao.find_all_menus(skip, limit)