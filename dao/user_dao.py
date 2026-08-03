from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from database.schema.user_schema import UserSchema


class UserDao:
    def __init__(self, database: Session):
        self.database = database

    def create(self, user: UserSchema) -> UserSchema:
        """
        Create a new user
        :param: user
        :return: user
        """
        self.database.add(user)
        self.database.commit()
        self.database.refresh(user)

        return user

    # O metodo abaixo pode ser usado para email, name, last_namem username,etc...
    def find_by_id(self, id: int) -> UserSchema | None:
        """
        Find a user by id
        :param: user_id
        :return: user
        """
        statement = select(UserSchema).where(UserSchema.id == id)
        return self.database.scalar(statement)


    def find_by_username(self, username: str) -> UserSchema | None:
        """
        Procura um utilizador pelo username.
        :param: username
        :return: user
        """
        statement = select(UserSchema).where(
            UserSchema.username == username
        )
        return self.database.scalar(statement)


    def find_by_email( self, email: str) -> UserSchema | None:
        """
        Procura um utilizador pelo email.
        :param: email
        :return: user
        """
        statement = select(UserSchema).where(
            UserSchema.email == email
        )

        return self.database.scalar(statement)

    def find_by_phone( self, phone: str) -> UserSchema | None:
        """
        Procura um utilizador pelo telefone.
        :param: phone
        :return: user
        """
        statement = select(UserSchema).where(
            UserSchema.phone == phone
        )

        return self.database.scalar(statement)

    def find_all(self, skip: int = 0, limit: int = 100) -> list[UserSchema]:
        """
        Retorna uma lista paginada de usuarios
        :param skip:
        :param limit:
        :return: list of users
        """
        st = (select(UserSchema).offset(skip).limit(limit).order_by(UserSchema.id))
        return self.database.scalars(st).all()



    def update(self, user: UserSchema) -> UserSchema:
        self.database.add(user)
        self.database.commit()
        self.database.refresh(user)

        return user

    def delete(self, user: UserSchema) -> None:
        """
        Remove permanentemente um utilizador.
        """
        self.database.delete(user)
        self.database.commit()

    def rollback(self) -> None:
        """
        Desfaz a transação atual.
        """

        self.database.rollback()
