from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import secrets

from dao.restaurante_dao import RestauranteDao
from dao.table_dao import TableDAO
from database.schema.table_schema import TableSchema
from models.table_model import TableCreate, TableResponse, TableUpdate


class TableService:
    def __init__(self, database: Session):
        self.table_dao = TableDAO(database)
        self.rest_dao = RestauranteDao(database)

    def create(self, table: TableCreate) -> TableResponse:
        restaurant = self.rest_dao.find_by_id(table.restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

        new_table = TableSchema(
            name=table.name,
            description=table.description,
            restaurant_id=restaurant.id,
        )
        try:
            return self.table_dao.create(new_table)
        except IntegrityError:
            self.table_dao.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Table already exists")

    def update(self, table_id: int, table_data: TableUpdate) -> TableSchema:
        table = self.table_dao.find_by_id(table_id)

        if not table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

        updated_table = table_data.model_dump(exclude_unset=True)

        if "name" in updated_table:
            name = updated_table["name"]
            if name == table.name:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Table name already exists")

        for field, value in updated_table.items():
            setattr(table, field, value)

        try:
            return self.table_dao.create(table)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Was not possible to update Table data")

    def find_all(self, skip, limit) -> list[TableResponse]:
        return self.table_dao.find_all(skip, limit)

    def find_all_restaurant_tables(self, restaurant_id: int, skip, limit) -> list[TableResponse]:
        return self.table_dao.find_tables_by_restaurant_id(restaurant_id, skip, limit)

    def rotate_public_token(self, table_id: int) -> TableSchema:
        table = self.table_dao.find_by_id(table_id)
        if not table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
        table.public_token = secrets.token_urlsafe(24)
        return self.table_dao.create(table)
