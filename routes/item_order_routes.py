from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from models.item_order import ItemOrderResponse, ItemOrderCreate
from service.item_order_service import ItemOrderService
from utils.data_base_engine import get_database
from service.security_service import require_roles

item_order_router = APIRouter(prefix="/item-order", tags=["Legacy Items in Order"], dependencies=[Depends(require_roles("admin"))], deprecated=True)

def get_item_order_service(database: Session = Depends(get_database)) -> ItemOrderService:
    return ItemOrderService(database)

@item_order_router.post("/register", response_model=ItemOrderResponse, status_code=status.HTTP_201_CREATED)
async def register(item_order: ItemOrderCreate, service: ItemOrderService = Depends(get_item_order_service)):
    return service.create(item_order)

@item_order_router.delete("/remove-item-in-order", status_code=status.HTTP_200_OK)
async def delete(item_order_id: int, service: ItemOrderService = Depends(get_item_order_service)):
    service.delete(item_order_id)
    return {
        "Message": f"Item {item_order_id} has been removed"
    }

