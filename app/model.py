from sqlalchemy import BigInteger, Column, Integer, String,Float
from app.service.database import Base

class Stock(Base):

    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol_origin = Column(String(20), unique=True, nullable=False)
    symbol = Column(String(20), unique=True)
    name_kor = Column(String(100))
    date_listing = Column(String(20))
    market_type = Column(String(50))
    stock_class = Column(String(50))
    par_value = Column(Integer, nullable=True)
    shares_listed = Column(BigInteger)

    def parse_par_value(val):
        try:
            return int(val)
        except (ValueError, TypeError):
            return None