import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Db_class(SqlAlchemyBase):
    """Отвечает за взаимодействие с базой"""
    __tablename__ = 'login_id_pairs'

    telegram_chat_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True)
    yandex_login = sqlalchemy.Column(sqlalchemy.String)