import secrets

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database.base import Base


class TableSchema(Base):
    __tablename__ = "table"
    
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String, nullable=False)
    description = Column("description", String, nullable=True)
    restaurant_id = Column("restaurant_id", Integer, ForeignKey("restaurant.id"), nullable=False)
    public_token = Column(String(64), nullable=False, unique=True, index=True, default=lambda: secrets.token_urlsafe(24))
    status = Column(Boolean, nullable=False, default=True)
    restaurant = relationship(
        "RestaurantSchema",
        back_populates="tables",
    )
    sessions = relationship("TableSessionSchema", back_populates="table")

    def __init__(self, name:str, restaurant_id:int,  description=None,):
        self.name = name
        self.description = description
        self.restaurant_id = restaurant_id
