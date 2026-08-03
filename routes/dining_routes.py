from fastapi import APIRouter, Depends, Header, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database.schema.user_schema import UserSchema
from models.dining_model import (
    ClientOrderCreate,
    DiningOrderResponse,
    PaymentConfirmation,
    PaymentRecordResponse,
    StaffOrderStatusUpdate,
    TableScanResponse,
    TableSessionCreate,
    TableSessionOpened,
    TableSessionSummary,
)
from models.menu_model import MenuResponse
from models.user_model import StaffRoleUpdate, UserResponse
from service.dining_service import DiningService
from service.security_service import require_roles
from service.realtime_service import realtime_manager
from utils.data_base_engine import get_database


public_router = APIRouter(prefix="/public", tags=["Public dining"])
staff_router = APIRouter(prefix="/staff", tags=["Staff dining"])
session_bearer = HTTPBearer(auto_error=True, scheme_name="TableSessionToken")


def get_dining_service(database: Session = Depends(get_database)) -> DiningService:
    return DiningService(database)


def get_table_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Security(session_bearer),
    service: DiningService = Depends(get_dining_service),
):
    return service.verify_session_token(credentials.credentials, session_id)


def build_summary(table_session) -> TableSessionSummary:
    return TableSessionSummary(
        session_id=table_session.public_id,
        status=table_session.status,
        table_name=table_session.table.name,
        total_amount=table_session.total_amount,
        opened_at=table_session.opened_at,
        checkout_requested_at=table_session.checkout_requested_at,
        closed_at=table_session.closed_at,
        orders=[DiningOrderResponse.model_validate(order) for order in table_session.orders],
    )


async def publish_to_session_and_restaurant(event_name: str, table_session, data) -> None:
    event = {"event": event_name, "data": data}
    await realtime_manager.broadcast(f"table:{table_session.public_id}", event)
    await realtime_manager.broadcast(f"restaurant:{table_session.restaurant_id}", event)


@public_router.get("/tables/{table_token}", response_model=TableScanResponse)
def scan_table(table_token: str, service: DiningService = Depends(get_dining_service)):
    table = service.scan_table(table_token)
    return TableScanResponse(
        restaurant_id=table.restaurant_id,
        restaurant_name=table.restaurant.name,
        table_name=table.name,
        table_token=table.public_token,
    )


@public_router.post("/table-sessions", response_model=TableSessionOpened, status_code=status.HTTP_201_CREATED)
async def open_table_session(data: TableSessionCreate, service: DiningService = Depends(get_dining_service)):
    table_session, table, token = service.open_session(data.table_token, data.customer_name)
    response = TableSessionOpened(
        session_id=table_session.public_id,
        session_token=token,
        status=table_session.status,
        restaurant_id=table_session.restaurant_id,
        table_name=table.name,
    )
    await realtime_manager.broadcast(
        f"restaurant:{table_session.restaurant_id}",
        {"event": "table_session.opened", "data": response.model_dump(mode="json", exclude={"session_token"})},
    )
    return response


@public_router.get("/table-sessions/{session_id}/menu", response_model=list[MenuResponse])
def get_menu(table_session=Depends(get_table_session), service: DiningService = Depends(get_dining_service)):
    return service.get_public_menu(table_session)


@public_router.post("/table-sessions/{session_id}/orders", response_model=DiningOrderResponse, status_code=201)
async def create_order(
    data: ClientOrderCreate,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=8, max_length=80),
    table_session=Depends(get_table_session),
    service: DiningService = Depends(get_dining_service),
):
    order = service.create_order(table_session, data, idempotency_key)
    response = DiningOrderResponse.model_validate(order)
    await publish_to_session_and_restaurant("order.created", table_session, response.model_dump(mode="json"))
    return response


@public_router.get("/table-sessions/{session_id}/summary", response_model=TableSessionSummary)
def session_summary(table_session=Depends(get_table_session)):
    return build_summary(table_session)


@public_router.post("/table-sessions/{session_id}/request-checkout", response_model=TableSessionSummary)
async def request_checkout(table_session=Depends(get_table_session), service: DiningService = Depends(get_dining_service)):
    service.request_checkout(table_session)
    response = build_summary(table_session)
    await publish_to_session_and_restaurant("table_session.checkout_requested", table_session, response.model_dump(mode="json"))
    return response


staff_member = require_roles("admin", "manager", "kitchen", "waiter", "cashier")
cashier = require_roles("admin", "manager", "cashier")
administrator = require_roles("admin")


@staff_router.get("/restaurants/{restaurant_id}/kitchen/orders", response_model=list[DiningOrderResponse])
def kitchen_orders(
    restaurant_id: int,
    user: UserSchema = Depends(staff_member),
    service: DiningService = Depends(get_dining_service),
):
    return service.list_kitchen_orders(restaurant_id, user)


@staff_router.patch("/orders/{order_id}/status", response_model=DiningOrderResponse)
async def update_order_status(
    order_id: int,
    data: StaffOrderStatusUpdate,
    user: UserSchema = Depends(staff_member),
    service: DiningService = Depends(get_dining_service),
):
    order = service.update_order_status(order_id, data.status, user)
    response = DiningOrderResponse.model_validate(order)
    await publish_to_session_and_restaurant("order.status_changed", order.table_session, response.model_dump(mode="json"))
    return response


@staff_router.post("/table-sessions/{session_id}/confirm-payment", response_model=PaymentRecordResponse)
async def confirm_payment(
    session_id: str,
    data: PaymentConfirmation,
    user: UserSchema = Depends(cashier),
    service: DiningService = Depends(get_dining_service),
):
    table_session = service.get_session_by_public_id(session_id)
    payment = service.confirm_payment(session_id, data, user)
    response = PaymentRecordResponse.model_validate(payment)
    await publish_to_session_and_restaurant(
        "table_session.closed",
        table_session,
        {"session_id": session_id, "status": "CLOSED", "payment": response.model_dump(mode="json")},
    )
    return response


@staff_router.patch("/users/{user_id}/role", response_model=UserResponse)
def assign_staff_role(
    user_id: int,
    data: StaffRoleUpdate,
    _admin: UserSchema = Depends(administrator),
    service: DiningService = Depends(get_dining_service),
):
    return service.assign_staff_role(user_id, data.user_type, data.restaurant_id)
