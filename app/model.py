
from sqlalchemy import (
    BigInteger, Column, Integer, String,Boolean,Float,
    DateTime,Date,func,UniqueConstraint)
from app.service.database import Base

# 주식종목 모델
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
    is_active = Column(Boolean, default=True)

    def parse_par_value(val):
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

# ETF종목 모델
class ETF(Base):

    __tablename__ = 'etfs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol_origin = Column(String(20), unique=True, nullable=False)
    symbol = Column(String(20), unique=True)
    name_kor = Column(String(100))
    date_listing = Column(String(20))
    base_market_type = Column(String(50))
    base_asset_type = Column(String(50))
    shares_outstanding = Column(BigInteger)
    is_active = Column(Boolean, default=True)

# 관심종목 모델
class Watchlist(Base):

    __tablename__ = 'watchlist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_type = Column(String(20))  # 'stock' or 'etf'
    asset_id = Column(String(20))  # references Stock.id or ETF.id
    is_watching = Column(Boolean, default=1)  # 1 for active, 0 for inactive
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    removed_at = Column(DateTime, nullable=True)

# 주가 모델
class DailyPrice(Base):

    __tablename__ = 'daily_price'

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(String(10), nullable=False) # FK to Stock.id or ETF.id
    date = Column(Date, nullable=False)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    trde_qty = Column(BigInteger) # 거래량
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)

    __table_args__ = (
        UniqueConstraint('stock_id','date', name = '_stock_date_uc'),
    )