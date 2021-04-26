import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Role(SqlAlchemyBase):
    __tablename__ = 'roles'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    roles = orm.relation("User", back_populates='user')
