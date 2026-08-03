from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from routes.auth_routes import get_user_service
from service.user_service import oauth2_schema, UserService
from utils.data_base_engine import get_database

# ===========================================================
# Quando nao precisamos de usar nenhum dado do usuario logado
# apenas pretendemos, bloquear as rotas e certificar que existe
# um usuario logado
# ===========================================================
test_router = APIRouter(
    prefix="/test",
    tags=["order"],
    dependencies=[Depends(oauth2_schema)],
)

@test_router.get("/pedido", status_code=status.HTTP_200_OK)
async def pedido():
    return {"message": "Hello World"}
# ===========================================================
# Rota bloqueada com dados do usuario
# ===========================================================
@test_router.get("/pedido-item", status_code=status.HTTP_200_OK)
async def pedido_item(token: str = Depends(oauth2_schema),  service: UserService = Depends(get_user_service)):
    user = service.verify_token(token)
    return {
        "message": "Hello World",
        "Last Name": user.last_name
    }


# ===========================================================
# Quando precisamos de usar algum dado do usuario logado,
# alem de pretendemos, bloquear a rota e certificar que e
# certificar da existencia de usuario logado
# ===========================================================
# test_router = APIRouter(
#     prefix="/test",
#     tags=["order"],
#     dependencies=[Depends(oauth2_schema)],
# )
#
# @test_router.get("/pedido", status_code=status.HTTP_200_OK)
# async def pedido(token: str = Depends(oauth2_schema),  service: UserService = Depends(get_user_service)):
#     user = service.verify_token(token)
#     return {
#         "message": "Hello World",
#         "Last Name": user.last_name
#     }
