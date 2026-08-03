from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

# ===========================================================
# Modelos de Menu
# ===========================================================
class MenuModel(BaseModel):
    name: str
    description: str | None = None

class MenuCreate(MenuModel):
    restaurant_id: int = Field(gt=0)

class MenuUpdate(BaseModel):
    name:str
    description:str | None = None
    profile_pic_url: str | None = None

class MenuResponse(MenuModel):
    id: int
    status: bool
    profile_pic_url: str | None = None
    restaurant_id:int
    created_at: datetime
    updated_at: datetime
    items: list[ItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(
        from_attributes=True
    )



# ===========================================================
# Modelos de Itens do Menu
# ===========================================================
class ItemModel(BaseModel):
    name: str
    price: float | None = None
    description: str | None = None
    profile_pic_url: str | None = None

class ItemCreate(ItemModel):
    menu_id: int = Field(gt=0)

class ItemUpdate(BaseModel):
    name:str
    price: float| None = None
    description: str | None = None
    profile_pic_url: str | None = None

class ItemResponse(ItemModel):
    id: int
    menu_id:int
    created_at: datetime
    updated_at: datetime
    ingredients: list[ItemIngredientResponse] = Field(default_factory=list)

    model_config = ConfigDict(
        from_attributes=True
    )






# ===========================================================
# Modelos de Ingredientes dos Itens do Menu
# ===========================================================
class IngredientModel(BaseModel):
    name: str


class IngredientCreate(IngredientModel):
    description: str

class IngredientUpdate(BaseModel):
    name: str
    description:str

class IngredientResponse(IngredientModel):
    id: int
    description: str
    created_at: datetime
    updated_at: datetime



# ===========================================================
# Modelos de Inggredientes dos Itens
# ===========================================================
class ItemIngredientModel(BaseModel):
    quantity: str
    description: str

class ItemIngredientCreate(ItemIngredientModel):
    item_id: int = Field(gt=0)
    ingredient_id: int = Field(gt=0)

class ItemIngredientUpdate(BaseModel):
    quantity: str
    description:str

class ItemIngredientResponse(ItemIngredientModel):
    id: int
    item_id: int
    ingredient_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )