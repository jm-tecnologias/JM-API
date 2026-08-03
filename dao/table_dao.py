from sqlalchemy import select
from sqlalchemy.orm import Session

from database.schema.table_schema import TableSchema
from models.table_model import TableCreate


class TableDAO:
    def __init__(self, database: Session):
        self. database = database

    def create(self, table: TableSchema) -> TableSchema:
        self.database.add(table)
        self.database.commit()
        self.database.refresh(table)
        return table

    def find_by_id(self, table_id: int) -> TableSchema | None:
        st = select(TableSchema).where(TableSchema.id == table_id)
        return self.database.scalar(st)

    def find_tables_by_restaurant_id(self, rest_id: int,
                                     skip:int = 0, limit:int = 0) -> list[TableSchema]:
        st = (select(TableSchema).offset(skip).limit(limit)
              .where(TableSchema.restaurant_id == rest_id)
              .order_by(TableSchema.name))
        return self.database.scalars(st).all()

    def find_all(self, skip:int = 0, limit:int = 0) -> list[TableSchema]:
        st = select(TableSchema).offset(skip).limit(limit).order_by(TableSchema.name)
        return self.database.scalars(st).all()

    def delete(self, table: TableSchema):
        self.database.delete(table)
        self.database.commit()
        self.database.refresh(table)

    def rollback(self) -> None:
        self.database.rollback()
