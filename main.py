from contextlib import asynccontextmanager
from routes.auth_routes import auth_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from routes.item_order_routes import item_order_router
from routes.item_routes import item_router
from routes.menu_routes import menu_router
from routes.order_routes import order_router
from routes.restaurant_routes import restaurant_router
from routes.table_routes import table_router
from routes.test_routes import test_router
from routes.dining_routes import public_router, staff_router
from routes.realtime_routes import realtime_router
# from utils.data_base_engine import create_database_tables



@asynccontextmanager
async def lifespan(app: FastAPI):
    # create_database_tables()
    yield

app = FastAPI(title="JM API", version="1.0.0", lifespan=lifespan)

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://127.0.0.1:3000,http://localhost:3000").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(restaurant_router)
app.include_router(menu_router)
app.include_router(item_router)
app.include_router(table_router)
app.include_router(order_router)
app.include_router(item_order_router)
# app.include_router(test_router)
app.include_router(public_router)
app.include_router(staff_router)
app.include_router(realtime_router)



@app.get("/")
def root():
    return {"message": "JM API is online."}


