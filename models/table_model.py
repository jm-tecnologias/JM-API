from pydantic import BaseModel, ConfigDict


class TableModel(BaseModel):
    name : str
    description: str | None = None

class TableCreate(TableModel):
    restaurant_id: int

class TableUpdate(BaseModel):
    name : str
    description: str | None = None

class TableResponse(TableModel):
    id : int
    restaurant_id : int
    public_token: str
    status: bool

    model_config = ConfigDict(from_attributes=True)
