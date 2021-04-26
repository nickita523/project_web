import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Categories(SqlAlchemyBase):
    __tablename__ = 'categories'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    categories = orm.relation("Goods", back_populates='goods')
