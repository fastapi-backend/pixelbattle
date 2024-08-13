from sqlalchemy import Column, String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)



class Battle(Base):
    __tablename__ = "battles"
    id = Column(Integer, primary_key=True)
    pixel = Column(String)
    color = Column(String)

