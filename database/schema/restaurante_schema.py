from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database.base import Base


class RestaurantSchema(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column("name", String, nullable=False, unique=True)
    description = Column("description", String, nullable=False)
    profile_pic_url = Column("profile_pic", String, nullable=True)
    status = Column("status", Boolean, nullable=False, default=True)
    created_at = Column("created_at", DateTime, nullable=False, default=datetime.now)
    updated_at = Column("updated_at", DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    menus = relationship(
        "MenuSchema",
        back_populates="restaurant",
        order_by="MenuSchema.name.asc()",
        cascade="all, delete-orphan",
    )
    tables = relationship(
        "TableSchema",
        back_populates="restaurant",
        order_by="TableSchema.name.asc()",
        cascade="all, delete-orphan",
    )

    def __init__(self,name,description,profile_pic_url=None):
        self.name = name
        self.description = description
        self.profile_pic_url = profile_pic_url

class RestaurantContactSchema(Base):
    __tablename__ = 'restaurant_contact'

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column("phone", String, nullable=False, unique=True)
    email = Column("email", String, nullable=True)
    website = Column("website", String, nullable=True)
    restaurant_id = Column("restaurant_id", Integer, ForeignKey("restaurant.id"), nullable=False)
    status = Column("status", Boolean, nullable=False, default=True)
    created_at = Column("created_at", DateTime, nullable=False, default=datetime.now)
    updated_at = Column("updated_at", DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, phone,email=None,website=None):
        self.phone = phone
        self.email = email
        self.website = website


class RestaurantAddressSchema(Base):
    __tablename__ = 'restaurant_address'

    id = Column(Integer, primary_key=True, autoincrement=True)
    province = Column("province", String, nullable=False )
    city = Column("city", String, nullable=False)
    nearby_hood = Column("nearby_hood", String, nullable=True)
    avenue = Column("avenue", String, nullable=True)
    number = Column("number", String, nullable=True)
    restaurant_id = Column("restaurant_id", Integer, ForeignKey("restaurant.id"), nullable=False)
    status = Column("status", Boolean, nullable=False, default=True)
    created_at = Column("created_at", DateTime, nullable=False, default=datetime.now)
    updated_at = Column("updated_at", DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self,province,city,nearby_hood=None,avenue=None,number=None):
        self.province = province
        self.city = city
        self.nearby_hood = nearby_hood
        self.avenue = avenue
        self.number = number
