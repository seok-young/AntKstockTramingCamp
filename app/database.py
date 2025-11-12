from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd

from app.core.config import settings

MYSQL_USER = settings.mysql_user
MYSQL_PASSWORD = settings.mysql_password
MYSQL_HOST = "ant-mysql"
MYSQL_PORT = settings.mysql_port
MYSQL_DB = settings.mysql_database

DATABASE_URL = settings.database_url


engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()





