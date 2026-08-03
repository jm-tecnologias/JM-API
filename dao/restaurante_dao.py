from sqlalchemy import select
from sqlalchemy.orm import Session

from database.schema.restaurante_schema import RestaurantSchema


class RestauranteDao:

    def __init__(self, database: Session):
        self.database = database

    def create(self, restaurant: RestaurantSchema) -> RestaurantSchema:
        self.database.add(restaurant)
        self.database.commit()
        self.database.refresh(restaurant)
        return restaurant

    def find_by_id(self, res_id: int) -> RestaurantSchema | None:
        st = select(RestaurantSchema).where(RestaurantSchema.id == res_id)
        return self.database.scalar(st)

    def find_by_name(self, name: str) -> RestaurantSchema | None:
        st = select(RestaurantSchema).where(RestaurantSchema.name == name)
        return self.database.scalar(st)

    def find_all(self, skip: int=0, limit: int=100) -> list[RestaurantSchema]:
        st = select(RestaurantSchema).offset(skip).limit(limit).order_by(RestaurantSchema.id)
        return self.database.scalars(st).all()

    def update(self, restaurant: RestaurantSchema) -> RestaurantSchema:
        self.database.add(restaurant)
        self.database.commit()
        self.database.refresh(restaurant)
        return restaurant

    def delete(self, restaurant: RestaurantSchema) -> None:
        self.database.delete(restaurant)
        self.database.commit()

    def rolllback(self) -> None:
        self.database.rollback()
