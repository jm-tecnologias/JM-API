from sqlalchemy import select
from sqlalchemy.orm import Session

from database.schema.user_history_schema import UserHistorySchema


class UserHistoryDAO:

    def __init__(self, database: Session):
        self.database = database

    def create(self, history: UserHistorySchema) -> UserHistorySchema:
        self.database.add(history)
        self.database.commit()
        self.database.refresh(history)
        return history

    def find_by_id(self, history_id: int) -> UserHistorySchema | None:
        st = (select(UserHistorySchema)
              .where(UserHistorySchema.id == history_id))
        return self.database.scalar(st)

    def find_by_user_id(self, user_id: int) -> list[UserHistorySchema]:
        st = (select(UserHistorySchema)
              .where(UserHistorySchema.user_id == user_id)
              .order_by(UserHistorySchema.accessed_at.desc()))
        return list(self.database.scalars(st).all())

    def delete(self, history: UserHistorySchema) -> None:
        self.database.delete(history)
        self.database.commit()
        self.database.refresh(history)
