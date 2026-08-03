from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class UserHistoryModel(BaseModel):
    action: str = Field(min_length=5, max_length=6)


class UserHistoryCreate(UserHistoryModel):
    user_id: int = Field(gt=0)


class UserHistoryResponse(UserHistoryModel):
    id: int
    user_id: int
    accessed_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

