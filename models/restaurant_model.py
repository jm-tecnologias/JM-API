from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from models.menu_model import MenuResponse

# ===========================================================
# Modelos de Restaurante
# ===========================================================
class RestaurantModel(BaseModel):
    name: str

class RestaurantCreate(RestaurantModel):
    description: str
    profile_pic_url: str | None

class RestaurantUpdate(BaseModel):
    name: str
    description: str | None = None
    profile_pic_url: str | None = None

class RestaurantResponse(RestaurantModel):
    id: int
    description: str | None = None
    status: bool
    profile_pic_url: str | None = None
    status: bool
    created_at: datetime
    updated_at: datetime
    menus:list[MenuResponse] = Field(default_factory=list)

    model_config = ConfigDict(
        from_attributes=True
    )


# ===========================================================
# Modelos de Contactos dos Restaurante
# ===========================================================
class RestaurantContactModel(BaseModel):
    phone: str
    email: EmailStr
    website: str

class RestaurantContactCreate(RestaurantContactModel):
    restaurant_id: int = Field(gt=0)

class RestaurantContactUpdate(BaseModel):
    phone: str
    email: EmailStr
    website: str

class RestaurantContactResponse(RestaurantContactModel):
    id: int
    restaurant_id: int
    status: bool
    created_at: datetime
    updated_at: datetime



# ===========================================================
# Modelos de Enderecos dos Restaurante
# ===========================================================
class RestaurantAddressModel(BaseModel):
    province: str
    city: str
    nearby_hood: str
    avenue:str
    number : int


class RestaurantAddressCreate(RestaurantAddressModel):
    restaurant_id: int = Field(gt=0)

class RestaurantAddressUpdate(BaseModel):
    province: str
    city: str
    nearby_hood: str
    avenue: str
    number: int


class RestaurantAddressResponse(RestaurantAddressModel):
    id: int
    restaurant_id: int
    status: bool
    created_at: datetime
    updated_at: datetime






