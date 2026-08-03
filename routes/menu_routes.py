from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

from models.menu_model import MenuResponse, MenuCreate, MenuUpdate
from service.menu_service import MenuService
from utils.data_base_engine import get_database
from service.security_service import require_roles

menu_router = APIRouter(prefix="/menus", tags=["Restaurants Menus"], dependencies=[Depends(require_roles("admin"))])

def get_menu_service(database: Session = Depends(get_database)) -> MenuService:
    return MenuService(database)

@menu_router.post("/register", response_model=MenuResponse, status_code=status.HTTP_201_CREATED)
async def register(menu: MenuCreate, service: MenuService = Depends(get_menu_service)):
    return service.create(menu)

@menu_router.patch("/update/{menu_id}", response_model=MenuResponse, status_code=status.HTTP_200_OK)
async def update(menu_id:int, menu: MenuUpdate, service: MenuService = Depends(get_menu_service)) ->MenuResponse:
    return service.update(menu_id, menu)

@menu_router.get("/list-all", response_model=list[MenuResponse], status_code=status.HTTP_200_OK)
async def list_all(skip: int = Query(default=0,ge=0),
                   limit: int = Query(default=100, ge=1, le=500),
                   service: MenuService = Depends(get_menu_service)) -> List[MenuResponse]:
    return service.find_all(skip=skip, limit=limit)

@menu_router.get("/list-by-restaurant-id/{restaurant_id}", response_model=list[MenuResponse], status_code=status.HTTP_200_OK)
async def list_by_restaurant_id(restaurant_id:int, skip: int = Query(default=0,ge=0),
                                limit: int = Query(default=100, ge=1, le=500),
                                service: MenuService = Depends(get_menu_service)) -> list[MenuResponse]:
    return service.find_all_restaurant_menus(restaurant_id, skip=skip, limit=limit)
