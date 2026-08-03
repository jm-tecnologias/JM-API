from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from models.order_model import OrderCreate, OrderResponse, OrderUpdate
from service.order_service import OrderService
from utils.data_base_engine import get_database
from service.security_service import require_roles

order_router = APIRouter(prefix="/order", tags=["Legacy Orders"], dependencies=[Depends(require_roles("admin"))], deprecated=True)

def get_order_service(database: Session = Depends(get_database)) -> OrderService:
    return OrderService(database)

@order_router.post("/register", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def register(order: OrderCreate, service: OrderService = Depends(get_order_service)) -> OrderResponse:
    return service.create(order)

@order_router.patch("/update/{order_id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
async def update(order_id:int, order: OrderUpdate, service: OrderService = Depends(get_order_service)) -> OrderResponse:
    return service.update(order_id, order)
