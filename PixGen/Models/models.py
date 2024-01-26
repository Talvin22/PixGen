from Database.database import Base
from sqlalchemy import Column, Integer, String


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    username = Column(String)
    count_gen_per_day = Column(Integer, default=3)
    balance = Column(Integer, default=0)





