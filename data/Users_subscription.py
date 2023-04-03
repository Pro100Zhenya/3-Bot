import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Users_subscription(SqlAlchemyBase):
    """Отвечает за взаимодействие с базой"""
    __tablename__ = 'subscription'
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True)
    user = sqlalchemy.Column(sqlalchemy.String)