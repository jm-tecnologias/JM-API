from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from database.base import Base


class MenuSchema(Base):
    __tablename__ = "menu"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String, nullable=False)
    description = Column("description", String, nullable=True)
    status = Column("status", Boolean, nullable=False, default=True)
    profile_pic_url = Column("profile_pic_url", String, nullable=True)
    restaurant_id = Column("restaurant_id", Integer, ForeignKey("restaurant.id"), nullable=False)
    created_at = Column("created_at", DateTime, nullable=False, default=datetime.now)
    updated_at = Column("updated_at", DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    restaurant = relationship(
        "RestaurantSchema",
        back_populates="menus",
    )
    items = relationship(
        "ItemSchema",
        back_populates="menu",
        order_by="ItemSchema.name.asc()",
        cascade="all, delete-orphan",
    )

    def __init__(self, name, restaurant_id, description=None,profile_pic_url=None):
        self.name = name
        self.restaurant_id = restaurant_id
        self.description = description
        self.profile_pic_url = profile_pic_url

class ItemSchema(Base):
    __tablename__ = "item"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String, nullable=False)
    description = Column("description", String, nullable=True)
    price = Column("price", Numeric(12, 2), nullable=False, default=0)
    profile_pic_url = Column("profile_pic_url", String, nullable=True)
    menu_id = Column("menu_id", Integer, ForeignKey("menu.id"), nullable=False)
    created_at = Column("created_at", DateTime, nullable=False, default=datetime.now)
    updated_at = Column("updated_at", DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    ingredients = relationship(
        "ItemIngredientSchema",
        back_populates="item",
        order_by="ItemIngredientSchema.id.asc()",
        cascade="all, delete-orphan",
    )
    menu = relationship(
        "MenuSchema",
        back_populates="items",
    )

    def __init__(self, name, menu_id, description=None, profile_pic_url=None, price=0.0):
        self.name = name
        self.description = description
        self.profile_pic_url = profile_pic_url
        self.menu_id = menu_id
        self.price = price

class IngredientSchema(Base):
    __tablename__ = "ingredient"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String, nullable=False)
    description = Column("description", String, nullable=True)
    created_at = Column("created_at", DateTime, nullable=False, default=datetime.now)
    updated_at = Column("updated_at", DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, name):
        self.name = name


class ItemIngredientSchema(Base):
    __tablename__ = "item_ingredient"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantity = Column("quantity", String, nullable=False) # quantidade descrita em string para que possa ser possiver passar numeros inteiros ou fraccionarios(ex: 2 ou 1/2)
    description = Column("description", String, nullable=True)
    item_id = Column("item_id", Integer, ForeignKey("item.id"), nullable=False)
    ingredient_id = Column("ingredient_id", Integer, ForeignKey("ingredient.id"), nullable=False)
    created_at = Column("created_at", DateTime, nullable=False, default=datetime.now)
    updated_at = Column("updated_at", DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    item = relationship(
        "ItemSchema",
        back_populates="ingredients",
    )

    def __init__(self, item_id, ingredient_id, quantity, description=None):
        self.item_id = item_id
        self.ingredient_id = ingredient_id
        self.quantity = quantity
        self.description = description


