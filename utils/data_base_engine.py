from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.base import Base

# Pasta raiz do projeto JM-API
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Pasta onde o SQLite será guardado
DATABASE_DIR = PROJECT_ROOT

# Cria a pasta caso não exista
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# Caminho completo do ficheiro
DATABASE_FILE = DATABASE_DIR / "data.db"

DATABASE_URL = f"sqlite:///{DATABASE_FILE.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread":False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

from database.schema.user_schema import UserSchema
from database.schema.user_history_schema import UserHistorySchema
from database.schema.restaurante_schema import RestaurantSchema
from database.schema.menu_schema import MenuSchema
from database.schema.table_schema import TableSchema
from database.schema.order_schema import OrderSchema
from database.schema.item_order_schema import ItemOrderSchema
from database.schema.table_session_schema import TableSessionSchema, PaymentRecordSchema
from database.schema.refresh_session_schema import RefreshSessionSchema

def get_database() -> Generator[Session, None, None]:
    """
    Cria uma sessão para cada requisição e fecha-a
    automaticamente no final.
    """
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


# def create_database_tables() -> None:
#     """
#     Importa os modelos e cria as tabelas registadas.
#     """
#     from database.schema.user_schema import UserSchema
#     from database.schema.user_history_schema import UserHistorySchema
#     from database.schema.restaurante_schema import RestaurantSchema
#     from database.schema.menu_schema import MenuSchema
#     from database.schema.table_schema import TableSchema
#     from database.schema.order_schema import OrderSchema
#     from database.schema.item_order_schema import ItemOrderSchema
#     from database.schema.table_session_schema import TableSessionSchema, PaymentRecordSchema
#
#     # print("Tabelas registadas:", list(Base.metadata.tables.keys()))
#     Base.metadata.create_all(bind=engine)
#     print("Base de dados criada com sucesso.")
#     # print(f"Localização: {DATABASE_FILE}")

