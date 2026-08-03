import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from jose import JWTError, jwt
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from database.schema.item_order_schema import ItemOrderSchema
from database.schema.menu_schema import ItemSchema, MenuSchema
from database.schema.order_schema import OrderSchema
from database.schema.table_schema import TableSchema
from database.schema.table_session_schema import PaymentRecordSchema, TableSessionSchema
from database.schema.user_schema import UserSchema
from database.schema.restaurante_schema import RestaurantSchema
from models.dining_model import ClientOrderCreate, OrderStatus, PaymentConfirmation, SessionStatus


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY") or ""
ALGORITHM = os.getenv("ALGORITHM") or "HS256"
SESSION_TOKEN_MINUTES = int(os.getenv("SESSION_TOKEN_EXPIRE_MINUTES", "480"))

ORDER_TRANSITIONS = {
    OrderStatus.SUBMITTED: {OrderStatus.ACCEPTED, OrderStatus.REJECTED, OrderStatus.CANCELLED},
    OrderStatus.ACCEPTED: {OrderStatus.PREPARING, OrderStatus.CANCELLED},
    OrderStatus.PREPARING: {OrderStatus.READY},
    OrderStatus.READY: {OrderStatus.SERVED},
    OrderStatus.SERVED: set(),
    OrderStatus.REJECTED: set(),
    OrderStatus.CANCELLED: set(),
}


class DiningService:
    def __init__(self, database: Session):
        self.database = database

    def scan_table(self, table_token: str) -> TableSchema:
        table = self.database.scalar(
            select(TableSchema)
            .options(selectinload(TableSchema.restaurant))
            .where(TableSchema.public_token == table_token, TableSchema.status.is_(True))
        )
        if not table or not table.restaurant.status:
            raise HTTPException(status_code=404, detail="Active table not found")
        return table

    def open_session(self, table_token: str, customer_name: str | None = None):
        table = self.scan_table(table_token)
        current = self.database.scalar(
            select(TableSessionSchema).where(
                TableSessionSchema.table_id == table.id,
                TableSessionSchema.active_key == "ACTIVE",
            )
        )
        if current is None:
            current = TableSessionSchema(
                restaurant_id=table.restaurant_id,
                table_id=table.id,
                customer_name=customer_name,
            )
            try:
                self.database.add(current)
                self.database.commit()
                self.database.refresh(current)
            except IntegrityError:
                self.database.rollback()
                current = self.database.scalar(
                    select(TableSessionSchema).where(
                        TableSessionSchema.table_id == table.id,
                        TableSessionSchema.active_key == "ACTIVE",
                    )
                )
                if current is None:
                    raise
        return current, table, self.create_session_token(current)

    @staticmethod
    def create_session_token(table_session: TableSessionSchema) -> str:
        now = datetime.now(timezone.utc)
        return jwt.encode(
            {
                "sub": table_session.public_id,
                "type": "table_session",
                "restaurant_id": table_session.restaurant_id,
                "table_id": table_session.table_id,
                "iat": now,
                "exp": now + timedelta(minutes=SESSION_TOKEN_MINUTES),
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

    def verify_session_token(self, token: str, public_id: str) -> TableSessionSchema:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "table_session" or payload.get("sub") != public_id:
                raise ValueError
        except (JWTError, TypeError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid or expired table session token")

        session = self.database.scalar(
            select(TableSessionSchema)
            .options(
                selectinload(TableSessionSchema.table),
                selectinload(TableSessionSchema.orders).selectinload(OrderSchema.items),
            )
            .where(TableSessionSchema.public_id == public_id)
        )
        if not session:
            raise HTTPException(status_code=404, detail="Table session not found")
        return session

    def get_public_menu(self, table_session: TableSessionSchema):
        return list(self.database.scalars(
            select(MenuSchema)
            .options(selectinload(MenuSchema.items))
            .where(MenuSchema.restaurant_id == table_session.restaurant_id, MenuSchema.status.is_(True))
            .order_by(MenuSchema.name)
        ).all())

    def get_session_by_public_id(self, public_id: str) -> TableSessionSchema:
        table_session = self.database.scalar(select(TableSessionSchema).where(TableSessionSchema.public_id == public_id))
        if not table_session:
            raise HTTPException(status_code=404, detail="Table session not found")
        return table_session

    def create_order(self, table_session: TableSessionSchema, data: ClientOrderCreate, request_key: str) -> OrderSchema:
        if table_session.status != SessionStatus.OPEN.value:
            raise HTTPException(status_code=409, detail="Session is not accepting orders")
        existing = self.database.scalar(select(OrderSchema).where(
            OrderSchema.table_session_id == table_session.id,
            OrderSchema.request_key == request_key,
        ))
        if existing:
            return self.get_order(existing.id)

        item_ids = {entry.item_id for entry in data.items}
        items = list(self.database.scalars(
            select(ItemSchema)
            .join(MenuSchema, ItemSchema.menu_id == MenuSchema.id)
            .where(ItemSchema.id.in_(item_ids), MenuSchema.restaurant_id == table_session.restaurant_id, MenuSchema.status.is_(True))
        ).all())
        item_map = {item.id: item for item in items}
        if len(item_map) != len(item_ids):
            raise HTTPException(status_code=400, detail="One or more items are unavailable or belong to another restaurant")

        order = OrderSchema(
            user_id=table_session.opened_by_user_id,
            table_id=table_session.table_id,
            order_status=OrderStatus.SUBMITTED.value,
            balance_amount=Decimal("0.00"),
        )
        order.table_session_id = table_session.id
        order.request_key = request_key
        try:
            self.database.add(order)
            self.database.flush()
            total = Decimal("0.00")
            for entry in data.items:
                item = item_map[entry.item_id]
                price = Decimal(str(item.price)).quantize(Decimal("0.01"))
                total += price * entry.quantity
                self.database.add(ItemOrderSchema(
                    order_id=order.id,
                    item_id=item.id,
                    quantity=entry.quantity,
                    unit_price=price,
                    item_name=item.name,
                    notes=entry.notes,
                    status=OrderStatus.SUBMITTED.value,
                ))
            order.balance_amount = total
            table_session.total_amount = Decimal(str(table_session.total_amount)) + total
            self.database.commit()
            return self.get_order(order.id)
        except IntegrityError:
            self.database.rollback()
            existing = self.database.scalar(select(OrderSchema).where(
                OrderSchema.table_session_id == table_session.id,
                OrderSchema.request_key == request_key,
            ))
            if existing:
                return self.get_order(existing.id)
            raise
        except Exception:
            self.database.rollback()
            raise

    def get_order(self, order_id: int) -> OrderSchema:
        order = self.database.scalar(
            select(OrderSchema).options(selectinload(OrderSchema.items)).where(OrderSchema.id == order_id)
        )
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    def list_kitchen_orders(self, restaurant_id: int, staff: UserSchema):
        self._assert_staff_restaurant(staff, restaurant_id)
        return list(self.database.scalars(
            select(OrderSchema)
            .join(TableSessionSchema, OrderSchema.table_session_id == TableSessionSchema.id)
            .options(selectinload(OrderSchema.items))
            .where(
                TableSessionSchema.restaurant_id == restaurant_id,
                OrderSchema.order_status.in_(["SUBMITTED", "ACCEPTED", "PREPARING", "READY"]),
            )
            .order_by(OrderSchema.created_at)
        ).all())

    def update_order_status(self, order_id: int, new_status: OrderStatus, staff: UserSchema) -> OrderSchema:
        order = self.get_order(order_id)
        if not order.table_session:
            raise HTTPException(status_code=409, detail="Legacy order has no table session")
        self._assert_staff_restaurant(staff, order.table_session.restaurant_id)
        current = OrderStatus(order.order_status)
        if new_status not in ORDER_TRANSITIONS[current]:
            raise HTTPException(status_code=409, detail=f"Invalid transition from {current.value} to {new_status.value}")
        if new_status in {OrderStatus.REJECTED, OrderStatus.CANCELLED}:
            order.table_session.total_amount = max(
                Decimal("0.00"),
                Decimal(str(order.table_session.total_amount)) - Decimal(str(order.balance_amount)),
            )
        order.order_status = new_status.value
        for item in order.items:
            item.status = new_status.value
        self.database.commit()
        return self.get_order(order.id)

    def request_checkout(self, table_session: TableSessionSchema):
        if table_session.status != SessionStatus.OPEN.value:
            raise HTTPException(status_code=409, detail="Checkout cannot be requested in the current state")
        pending = {OrderStatus.SUBMITTED.value, OrderStatus.ACCEPTED.value, OrderStatus.PREPARING.value, OrderStatus.READY.value}
        if any(order.order_status in pending for order in table_session.orders):
            raise HTTPException(status_code=409, detail="There are orders not yet served")
        table_session.status = SessionStatus.CHECKOUT_REQUESTED.value
        table_session.checkout_requested_at = datetime.now()
        self.database.commit()
        return table_session

    def confirm_payment(self, public_id: str, data: PaymentConfirmation, staff: UserSchema):
        table_session = self.database.scalar(
            select(TableSessionSchema).where(TableSessionSchema.public_id == public_id)
        )
        if not table_session:
            raise HTTPException(status_code=404, detail="Table session not found")
        self._assert_staff_restaurant(staff, table_session.restaurant_id)
        if table_session.status not in {SessionStatus.CHECKOUT_REQUESTED.value, SessionStatus.PAYMENT_PENDING.value}:
            raise HTTPException(status_code=409, detail="Session is not awaiting payment")
        expected = Decimal(str(table_session.total_amount)).quantize(Decimal("0.01"))
        received = data.amount_received.quantize(Decimal("0.01"))
        if received != expected:
            raise HTTPException(status_code=409, detail=f"Amount must equal session total: {expected}")
        try:
            payment = PaymentRecordSchema(
                table_session_id=table_session.id,
                method=data.method,
                amount=received,
                external_reference=data.external_reference,
                notes=data.notes,
                confirmed_by_user_id=staff.id,
            )
            self.database.add(payment)
            table_session.status = SessionStatus.CLOSED.value
            table_session.active_key = None
            table_session.closed_at = datetime.now()
            for order in table_session.orders:
                order.payment_status = True
            self.database.commit()
            self.database.refresh(payment)
            return payment
        except Exception:
            self.database.rollback()
            raise

    def assign_staff_role(self, user_id: int, role: str, restaurant_id: int | None):
        user = self.database.get(UserSchema, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if role not in {"admin", "client"}:
            if restaurant_id is None or not self.database.get(RestaurantSchema, restaurant_id):
                raise HTTPException(status_code=400, detail="A valid restaurant is required for this role")
        user.user_type = role
        user.restaurant_id = None if role in {"admin", "client"} else restaurant_id
        self.database.commit()
        self.database.refresh(user)
        return user

    @staticmethod
    def _assert_staff_restaurant(staff: UserSchema, restaurant_id: int):
        if staff.user_type == "admin":
            return
        if staff.restaurant_id != restaurant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Staff member belongs to another restaurant")
