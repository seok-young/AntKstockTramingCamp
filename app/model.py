
from sqlalchemy import (
    BigInteger, Column, Integer, String,Boolean,Float,
    DateTime,Date,func,UniqueConstraint,CheckConstraint,ForeignKey)
from datetime import datetime

from app.core.database import Base



# 투자종목(stock + etf) 모델
class Ticker(Base):

    __tablename__ = 'ticker'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol_origin = Column(String(20), unique=True, nullable=False)
    symbol = Column(String(20), unique=True)
    name_kor = Column(String(100))
    asset_type = Column(String(20))
    market_type = Column(String(50))
    date_listing = Column(String(20))
    total_shares = Column(BigInteger)
    is_active = Column(Boolean, default=True)


# 관심종목 모델
class Watchlist(Base):

    __tablename__ = 'watchlist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_type = Column(String(20))  # 'stock' or 'etf'
    ticker_symbol = Column(String(20), ForeignKey('ticker.symbol'))  
    is_watching = Column(Boolean, default=1)  # 1 for active, 0 for inactive
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    removed_at = Column(DateTime, nullable=True)

# 주가 모델
class DailyPrice(Base):

    __tablename__ = 'daily_price'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_symbol = Column(String(10), ForeignKey('ticker.symbol'), nullable=False) 
    date = Column(Date, nullable=False)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    trde_qty = Column(BigInteger) # 거래량
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)

    __table_args__ = (
        UniqueConstraint('ticker_symbol','date', name = '_ticker_date_uc'),
    )

# 지표 모델
class Analysis(Base):

    __tablename__ = 'analysis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_symbol = Column(String(10), ForeignKey('ticker.symbol'), nullable=False) 
    date = Column(Date, nullable=False)
    close_price = Column(Float)
    ma5 = Column(Float)
    ma20 = Column(Float)
    ma60 = Column(Float)
    ma120 = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_hist = Column(Float)
    rsi = Column(Float)
    bb_middle = Column(Float)
    bb_upper = Column(Float)
    bb_lower = Column(Float)

    __table_args__ = (
        UniqueConstraint('ticker_symbol','date', name = '_ticker_date_uc'),
        CheckConstraint('close_price >= 0', name='check_close_price_positive'),
        CheckConstraint('ma5 >= 0', name='check_ma5_positive'),
        CheckConstraint('ma20 >= 0', name='check_ma20_positive'),
        CheckConstraint('ma120 >= 0', name='check_ma120_positive'),
        CheckConstraint('rsi >= 0 AND rsi <= 100', name='check_rsi_range'),
    )

# 추천 모델
class Recommendation(Base):

    __tablename__ = 'recommendation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_symbol = Column(String(10), ForeignKey('ticker.symbol'), nullable=False) 
    analysis_id = Column(String(10), nullable=False)
    signal_type = Column(String(10), nullable=False)
    strategy_name = Column(String(50), default='BASIC')
    base_date = Column(Date, index=True)
    price = Column(Float)
    is_sent = Column(Boolean, default=0)
    create_at= Column(DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint('ticker_symbol', 'base_date', 'signal_type', name='_ticker_signal_uc'),
    )