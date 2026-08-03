from fastapi import APIRouter, Depends, Header, Request, Response, Security, status
from sqlalchemy.orm import Session
from models.user_model import BootstrapAdminRequest, RefreshSessionResponse, UserCreate, UserResponse, UserUpdate, TokenResponse
from database.schema.user_schema import UserSchema
from utils.data_base_engine import get_database
from service.user_service import UserService, oauth2_schema
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm
from service.security_service import get_current_user


auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
refresh_bearer = HTTPBearer(scheme_name="RefreshToken")

def get_user_service(database: Session = Depends(get_database)) -> UserService:
    return UserService(database)


@auth_router.post("/sign-up", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(user: UserCreate, service: UserService = Depends(get_user_service)) -> UserResponse:
    return service.create(user)


@auth_router.post("/bootstrap-admin", response_model=UserResponse)
def bootstrap_admin(
    data: BootstrapAdminRequest,
    bootstrap_key: str = Header(alias="X-Bootstrap-Key"),
    service: UserService = Depends(get_user_service),
):
    return service.bootstrap_admin(data.username, bootstrap_key)

@auth_router.post("/sign-in", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def sign_in(
    request: Request,
    credentials: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
):
    user = service.get_user_login(credentials.username, credentials.password)
    access_token = service.create_token(user.id, user)
    refresh_token = service.issue_refresh_token(
        user,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@auth_router.post("/refresh", response_model=TokenResponse)
async def use_refresh_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(refresh_bearer),
    service: UserService = Depends(get_user_service),
):
    user, new_refresh_token = service.rotate_refresh_token(
        credentials.credentials,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    user_response = UserResponse.model_validate(user)
    access_token = service.create_token(user.id,user_response)
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: HTTPAuthorizationCredentials = Security(refresh_bearer),
    service: UserService = Depends(get_user_service),
):
    service.revoke_refresh_token(credentials.credentials)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@auth_router.post("/logout-all")
def logout_all(
    user: UserSchema = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    revoked = service.revoke_all_refresh_sessions(user.id)
    return {"revoked_sessions": revoked}


@auth_router.get("/sessions", response_model=list[RefreshSessionResponse])
def list_sessions(
    user: UserSchema = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return [
        RefreshSessionResponse(
            id=session.public_id,
            issued_at=session.issued_at,
            expires_at=session.expires_at,
            last_used_at=session.last_used_at,
            user_agent=session.user_agent,
            ip_address=session.ip_address,
        )
        for session in service.list_refresh_sessions(user.id)
    ]


@auth_router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_session(
    session_id: str,
    user: UserSchema = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    service.revoke_refresh_session_by_public_id(user.id, session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@auth_router.patch("/update/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update(user_data: UserUpdate,
                 token: str = Depends(oauth2_schema),
                 service: UserService = Depends(get_user_service)) -> UserResponse:
    user = service.verify_token(token)
    return service.update_user(user.id, user_data)






















































# def get_user_service(
#     database: Session = Depends(get_database)
# ) -> UserService:
#     """
#     Cria uma instância de ``UserService`` associada à sessão de base de dados
#     da requisição atual.
#
#     A sessão é fornecida automaticamente pelo sistema de dependências do
#     FastAPI através da função ``get_database``.
#
#     :param:
#         database: Sessão SQLAlchemy utilizada para executar operações
#             na base de dados.
#
#     :returns:
#         Uma instância de ``UserService`` configurada com a sessão atual.
#     """
#     return UserService(database)
#
#
# @auth_router.post(
#     "/sign-up",
#     response_model=UserResponse,
#     status_code=status.HTTP_201_CREATED
# )
# async def sign_up(
#     user: UserCreate,
#     service: UserService = Depends(get_user_service)
# ) -> UserResponse:
#     """
#     Regista um novo utilizador no sistema.
#
#     Os dados do utilizador devem ser enviados no corpo da requisição em
#     formato JSON e devem obedecer à estrutura definida por `UserCreate:`.
#
#     `:param:`
#         `user:` Dados necessários para criar a conta do utilizador.\n
#             user:
#             {
#               "username": "string",
#               "name": "string",
#               "last_name": "string",
#               "email": "user@example.com",
#               "phone": "stringstr",
#               "password": "stringstr"
#             }.
#     `:param:`
#         `service:` Serviço responsável pelas regras de negócio relacionadas com os utilizadores.
#
#     `:return:`
#         `UserResponse:` Os dados do utilizador criado, de acordo com o modelo\n
#             UserResponse:
#             {
#               "username": "string",
#               "name": "string",
#               "last_name": "string",
#               "email": "user@example.com",
#               "phone": "stringstr",
#               "id": 0,
#               "status": true,
#               "created_at": "2026-07-23T13:21:11.975Z",
#               "updated_at": "2026-07-23T13:21:11.975Z",
#               "histories":
#               [
#                 {
#                   "action": "string",
#                   "id": 0,
#                   "user_id": 0,
#                   "accessed_at": "2026-07-23T13:21:11.975Z"
#                 }
#               ]
#             }
#
#     `:raises:`
#         `HTTPException`\n
#     `HTTPException:`\n
#      Caso os dados sejam inválidos, o nome de utilizador já exista ou ocorra algum erro durante o registo.
#     """
#     # user_created = service.create(user)
#     # response = UserResponse.model_validate(user_created)
#     # return response.model_copy(
#     #     update={"token": service.create_token(user_created.id)}
#     # )
#     return service.create(user)

# @auth_router.get(
#     "/sign-in/{username,password}",
#     response_model=UserResponse,
#     status_code=status.HTTP_200_OK
# )
# async def sign_in(
#     username: str,
#     password: str,
#     service: UserService = Depends(get_user_service)
# ) -> UserResponse:
#     """
#     Autentica um utilizador através do nome de utilizador e da palavra-passe.
#
#     O serviço verifica se existe um utilizador com as credenciais fornecidas
#     e devolve os respetivos dados quando a autenticação for bem-sucedida.
#
#     :param:
#         username: Nome de utilizador utilizado para iniciar sessão.
#         password: Palavra-passe associada à conta do utilizador.
#         service: Serviço responsável pela validação das credenciais.
#
#     :returns:
#         Os dados do utilizador autenticado, de acordo com o modelo
#         ``UserResponse``.
#
#     :raise:
#         HTTPException: Caso o utilizador não exista ou as credenciais sejam
#             inválidas.
#     """
#     return service.get_user_login(username, password)

# @auth_router.post(
#     "/sign-in",
#     # response_model=json,
#     status_code=status.HTTP_200_OK
# )
# async def sign_in(credentials: OAuth2PasswordRequestForm = Depends(), service: UserService = Depends(get_user_service)):
# # async def sign_in(credentials: UserLogin, service: UserService = Depends(get_user_service)):
# # async def sign_in(credentials: UserLogin, service: UserService = Depends(get_user_service)) -> UserResponse:
#     """
#     Autentica um utilizador no sistema.
#
#     As credenciais são recebidas no corpo da requisição em formato JSON,
#     evitando a exposição da palavra-passe na URL.
#     O serviço verifica se existe um utilizador com as credenciais fornecidas
#     e devolve os respetivos dados quando a autenticação for bem-sucedida.
#
#     `:param:`
#         `credentials:` Contem Nome de utilizador utilizado para iniciar sessão.
#         e Palavra-passe associada à conta do utilizador.\n
#         credentials:
#         {
#           "username": "string",
#           "password": "stringst"
#         }
#     `:param:`
#         `service:` Serviço responsável pela validação das credenciais.
#
#     `:returns:`
#         `UserResponse`
#         Os dados do utilizador autenticado, de acordo com o modelo.\n
#         `UserResponse`
#         {
#             "username": "string",
#             "name": "string",
#             "last_name": "string",
#             "email": "user@example.com",
#             "phone": "stringstr",
#             "id": 0,
#             "status": true,
#             "created_at": "2026-07-23T13:21:11.975Z",
#             "updated_at": "2026-07-23T13:21:11.975Z",
#             "histories":[
#                 {
#                 "action": "string",
#                 "id": 0,
#                 "user_id": 0,
#                 "accessed_at": "2026-07-23T13:21:11.975Z"
#                 }
#             ]
#         }
#    `:raises:`
#         `HTTPException`\n
#    `HTTPException:`\n
#    Caso as credenciais fornecidas sejam inválidas.
#    """
#     user = service.get_user_login(credentials.username, credentials.password)
#     # if not user:
#     #     raise "+++++++++++++++++++++++++++++++++++++++++++++++++++sdsd"
#     # else:
#     access_token = service.create_token(user.id, user)
#     # refresh_token = service.create_token(user.id, user, token_duration=timedelta(hours=2))
#     return {
#         "access_token": access_token,
#         # "refresh_token": refresh_token,
#         "token_type": "bearer"
#     }
#     # user = service.get_user_login(credentials.username, credentials.password)
#     # return user
#
#
# @auth_router.get("/refresh")
# # async def use_refresh_toke(token, service: UserService = Depends(get_user_service)):
# async def use_refresh_token(token: str = Depends(oauth2_schema), service: UserService = Depends(get_user_service)):
#     user = service.verify_token(token)
#     user_response = UserResponse.model_validate(user)
#     access_token = service.create_token(user.id,user_response)
#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#     }
#
#
# @auth_router.patch(
#     "/update/{user_id}",
#     response_model=UserResponse,
#     status_code=status.HTTP_200_OK
# )
# async def update(
#     user_id: int,
#     user: UserUpdate,
#     service: UserService = Depends(get_user_service)
# ) -> UserResponse:
#     """
#     Atualiza parcialmente os dados de um utilizador existente.
#
#     Apenas os campos enviados no corpo da requisição serão
#     alterados. Os campos não informados manterão os seus
#     valores atuais.
#
#     `:param:`
#         `user_id:` Identificador único do utilizador que será atualizado.
#
#     `:param:`
#         `user:` Dados que serão atualizados. O objeto deve ser enviado
#         no corpo da requisição em formato JSON.\n
#         user:
#         {
#           "username": "string",
#           "password": "stringst",
#           "name": "string",
#           "last_name": "string",
#           "email": "user@example.com",
#           "phone": "stringstr",
#         }
#
#     `:param`
#         `service:` Serviço responsável por validar os dados, localizar o
#         utilizador e executar a atualização.
#
#     `:return:`
#         `UserResponse`
#         Dados atualizados do utilizador.\n
#         UserResponse
#         {
#             "username": "string",
#             "name": "string",
#             "last_name": "string",
#             "email": "user@example.com",
#             "phone": "stringstr",
#             "id": 0,
#             "status": true,
#             "created_at": "2026-07-23T13:21:11.975Z",
#             "updated_at": "2026-07-23T13:21:11.975Z",
#             "histories":[
#                     {
#                     "action": "string",
#                     "id": 0,
#                     "user_id": 0,
#                     "accessed_at": "2026-07-23T13:21:11.975Z"
#                     }
#                 ]
#             }
#
#     `:raises:`
#         `HTTPException`\n
#     `HTTPException:`\n
#     `404` — Quando o utilizador não for encontrado.\n
#     `409` — Quando o username, email ou telefone informado já estiver associado a outro utilizador.\n
#     `422` — Quando os dados enviados não cumprirem as validações definidas em UserUpdate.
#     """
#     return service.update_user(user_id, user)
