from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dao.restaurante_dao import RestauranteDao
from database.schema.restaurante_schema import RestaurantSchema
from models.restaurant_model import RestaurantCreate, RestaurantResponse, RestaurantUpdate

class RestaurantService:
    def __init__(self, database: Session):
        self.dao = RestauranteDao(database)

    def create(self, restaurant: RestaurantCreate) -> RestaurantResponse:
        existing_name = self.dao.find_by_name(restaurant.name)
        if existing_name:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Restaurant with that name already exists")

        new_restaurant = RestaurantSchema(
            name= restaurant.name,
            description= restaurant.description,
            profile_pic_url=restaurant.profile_pic_url,
        )
        return self.dao.create(new_restaurant)

    def update(self,restaurant_id:int, restaurant_data: RestaurantUpdate) -> RestaurantSchema:
        restaurant = self.dao.find_by_id(restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

        updated_data = restaurant_data.model_dump(exclude_unset=True)
        if "name" in updated_data:
            name = updated_data["name"]
            if name == restaurant.name:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Name already exists")

        for field, value in updated_data.items():
            setattr(restaurant, field, value)
        try:
            return self.dao.update(restaurant)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Was not posssible to update this restaurant data")


    def find_all(self, skip, limit) -> list[RestaurantSchema]:
        return self.dao.find_all(skip=skip, limit=limit)

    def find_by_id(self, rest_id):
        return self.dao.find_by_id(rest_id)
