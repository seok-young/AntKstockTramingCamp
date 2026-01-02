from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd

from app.core.config import settings

MYSQL_USER = settings.MYSQL_USER
MYSQL_PASSWORD = settings.MYSQL_PASSWORD
MYSQL_HOST = "ant-mysql"
# MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = settings.MYSQL_PORT
MYSQL_DB = settings.MYSQL_DATABASE

DATABASE_URL = settings.database_url


engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()





