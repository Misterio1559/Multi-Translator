import datetime
import sqlalchemy
from data.sql import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'Users'
    User_id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    Language = sqlalchemy.Column(sqlalchemy.String, default='en')
    Translating = sqlalchemy.Column(sqlalchemy.String, default='on')
