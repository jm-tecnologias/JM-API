from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from dao.user_dao import UserDao
from dao.user_history_dao import UserHistoryDAO
from database.schema.user_history_schema import UserHistorySchema
from models.user_history_model import UserHistoryCreate


class UserHistoryService:

    def __init__(self, database: Session):
        self.user_dao = UserDao(database)
        self.history_dao = UserHistoryDAO(database)

    def create_history(self, history_date: UserHistoryCreate) -> UserHistorySchema:
        user = self.user_dao.find_by_id(history_date.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        new_history = UserHistorySchema(
            user_id=history_date.user_id,
            action=history_date.action
        )

        return self.history_dao.create(new_history)

    def get_user_history(self, user_id: int) -> list[UserHistorySchema]:
        user = self.user_dao.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return self.history_dao.find_by_user_id(user.id)