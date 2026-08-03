from database.base import Base
from datetime import datetime
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String)
from sqlalchemy.orm import relationship


class UserSchema(Base):
    __tablename__ = "user"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    username = Column("username", String,  nullable=False, unique=True)
    password = Column("password", String, nullable=False)
    name = Column("name", String, nullable=False)
    last_name = Column("last_name", String, nullable=False)
    email = Column("email", String, nullable=False)
    phone = Column("phone", String, nullable=False, unique=True)
    profile_pic_url = Column("profile_pic_url", String, nullable=True)
    user_type = Column("user_type", String, nullable=False, default="client")
    restaurant_id = Column(Integer, ForeignKey("restaurant.id"), nullable=True)
    status = Column("status", Boolean, nullable=False, default=True)
    created_at = Column("created_at", DateTime, nullable=False, default=datetime.now)
    updated_at = Column("updated_at", DateTime,  nullable=False, default=datetime.now, onupdate=datetime.now)
    histories = relationship(
        "UserHistorySchema",
        back_populates="user",
        order_by="UserHistorySchema.accessed_at.desc()",
        cascade="all, delete-orphan",
    )

    def __init__(self, username, password, name,last_name,email,phone):
        self.username = username
        self.password = password
        self.name = name
        self.last_name = last_name
        self.email = email
        self.phone = phone







