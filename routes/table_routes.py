import io
import os

import qrcode
from fastapi import APIRouter, Depends, status, Query, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from models.table_model import TableResponse, TableCreate, TableUpdate
from service.table_service import TableService
from utils.data_base_engine import get_database
from service.security_service import require_roles

table_router = APIRouter(prefix="/tables", tags=["Tables"], dependencies=[Depends(require_roles("admin"))])

def get_table_service(database: Session = Depends(get_database)) ->TableService:
    return TableService(database)

@table_router.post("/register", response_model=TableResponse, status_code=status.HTTP_201_CREATED)
async def register(table: TableCreate, service: TableService = Depends(get_table_service)):
    return service.create(table)

@table_router.patch("/update/{table_id}", response_model=TableResponse, status_code=status.HTTP_200_OK)
async def update(table_id:int, table: TableUpdate, service: TableService = Depends(get_table_service)) -> TableResponse:
    return service.update(table_id, table)

@table_router.get("/list-all", response_model=list[TableResponse], status_code=status.HTTP_200_OK)
async def list_all(skip: int = Query(default=0, ge=0),
                   limit:int = Query(default=100, ge=1, le=500),
                   service: TableService = Depends(get_table_service)) -> list[TableResponse]:
    return service.find_all(skip, limit)

@table_router.get("/list-by-restaurant-id/{restaurant_id}", response_model=list[TableResponse], status_code=status.HTTP_200_OK)
async def list_by_restaurant_id(restaurant_id: int, skip:int = Query(default=0, ge=0),
                                limit:int = Query(default=100, ge=1, le=500),
                                service: TableService = Depends(get_table_service)) -> list[TableResponse]:
    return service.find_all_restaurant_tables(restaurant_id, skip, limit)


@table_router.get("/{table_id}/qr", response_class=Response)
def table_qr(table_id: int, service: TableService = Depends(get_table_service)):
    table = service.table_dao.find_by_id(table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    client_base_url = os.getenv("PUBLIC_CLIENT_BASE_URL", "http://127.0.0.1:3000")
    target = f"{client_base_url.rstrip('/')}/t/{table.public_token}"
    image = qrcode.make(target)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return Response(
        content=buffer.getvalue(),
        media_type="image/png",
        headers={"Content-Disposition": f'inline; filename="table-{table.id}-qr.png"'},
    )


@table_router.post("/{table_id}/rotate-token", response_model=TableResponse)
def rotate_table_token(table_id: int, service: TableService = Depends(get_table_service)):
    return service.rotate_public_token(table_id)
