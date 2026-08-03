from datetime import datetime
from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String)
from sqlalchemy.orm import relationship

from database.base import Base

class UserHistorySchema(Base):
    __tablename__ = "user_history"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    user_id = Column("user_id", Integer, ForeignKey("user.id"), nullable=False)
    action = Column("action", String, nullable=False)
    accessed_at = Column("accessed_at", DateTime, default=datetime.now, nullable=False)
    user = relationship(
        "UserSchema",
        back_populates="histories",
    )

    def __init__(self, user_id, action):
        self.user_id = user_id
        self.action = action
