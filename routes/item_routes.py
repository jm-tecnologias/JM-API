from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from models.menu_model import MenuResponse, ItemResponse, ItemCreate, ItemUpdate
from service.item_service import ItemService
from utils.data_base_engine import get_database
from service.security_service import require_roles

item_router = APIRouter(prefix="/items", tags=["Menu items"], dependencies=[Depends(require_roles("admin"))])

def get_item_service(database: Session = Depends(get_database)) -> ItemService:
    return ItemService(database)

@item_router.post("/register", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def register(item: ItemCreate, service: ItemService = Depends(get_item_service)) -> ItemResponse:
    return service.create_item(item)

@item_router.patch("/update/{item_id}", response_model=ItemResponse, status_code=status.HTTP_200_OK)
async def update(item_id: int, item: ItemUpdate, service: ItemService = Depends(get_item_service)) -> ItemResponse:
    return service.update(item_id, item)

@item_router.get("/list-all", response_model=list[ItemResponse], status_code=status.HTTP_200_OK )
async def list_all(skip: int = Query(default=0, ge=0),
                   limit: int = Query(default=100, ge=1, le=500),
                   service: ItemService = Depends(get_item_service)) -> list[ItemResponse]:
    return service.find_all_items(skip, limit)

@item_router.get("/list-by-menu-id/{menu_id}", response_model=list[ItemResponse], status_code=status.HTTP_200_OK )
async def list_by_menu_id(menu_id: int,
                          skip: int = Query(default=0, ge=0),
                          limit: int = Query(default=100, ge=1, le=500),
                          service: ItemService = Depends(get_item_service)) -> list[ItemResponse]:
    return service.find_all_menu_items(menu_id, skip, limit)

