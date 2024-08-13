from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("PIXELBATTLE_DB_URL")

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)