from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

from models.restaurant_model import RestaurantResponse, RestaurantCreate, RestaurantUpdate
from service.restaurant_service import RestaurantService
from utils.data_base_engine import get_database
from service.security_service import require_roles

restaurant_router = APIRouter(prefix="/restaurants", tags=["Restaurants"], dependencies=[Depends(require_roles("admin"))])

def get_restaurant_service(database: Session = Depends(get_database)) -> RestaurantService:
    return RestaurantService(database)

@restaurant_router.post("/register", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
async def register(restaurant: RestaurantCreate, service: RestaurantService = Depends(get_restaurant_service)) -> RestaurantResponse:
    return service.create(restaurant)

@restaurant_router.patch("/updade/{restaurant_id}", response_model=RestaurantResponse, status_code=status.HTTP_200_OK)
async def update(restaurant_id: int,
                 restaurant_data: RestaurantUpdate,
                 service: RestaurantService = Depends(get_restaurant_service)) -> RestaurantResponse:
    return service.update(restaurant_id, restaurant_data)

@restaurant_router.get("/list-all", response_model=List[RestaurantResponse], status_code=status.HTTP_200_OK)
async def list_all(skip: int = Query(default=0, ge=0),
                  limit:int = Query(default=100, ge=1, le=500),
                  service: RestaurantService = Depends(get_restaurant_service)) -> List[RestaurantResponse]:
    return service.find_all(skip=skip, limit=limit)

# @restaurant_router.get("/find-by-od/{rest_id}", response_model=RestaurantResponse, status_code=status.HTTP_200_OK)
# async def update(rest_id: int, service: RestaurantService = Depends(get_restaurant_service)) -> RestaurantResponse:
#     return service.find_by_id(rest_id)
