from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import datetime as dt

# 티커 입력 구조 정의
class TickerCreate(BaseModel):
    symbol_origin: str = Field(..., max_length=20, description="원본 종목 코드")
    symbol: Optional[str] = Field(None, max_length=20)
    name_kor: Optional[str] = Field(None, max_length=100)    
    asset_type: Optional[str] = Field(None, max_length=20)
    market_type: Optional[str] = Field(None, max_length=50)
    date_listing: Optional[str] = Field(None, max_length=20)    
    total_shares: Optional[int] = Field(None)    
    is_active: bool = Field(default=True)

    model_config = ConfigDict(from_attributes=True)

# 관심종목 입력 구조 정의
class WatchlistCreate(BaseModel):
    asset_type: str = Field(None, max_length=20, description="'stock' or 'etf'")
    ticker_symbol: str = Field(..., max_length=20)
    is_watching: bool = Field(default=True)
    created_at: dt.datetime
    removed_at: Optional[dt.datetime] = None

    model_config = ConfigDict(from_attributes=True)

# 종가 입력 구조 정의
class DailyPriceCreate(BaseModel):
    ticker_symbol: str = Field(..., max_length=10, description="종목 코드")
    date: dt.date = Field(..., description="거래 일자")
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None    
    trde_qty: Optional[int] = None    
    created_at: dt.datetime
    updated_at: Optional[dt.datetime] = None

    model_config = ConfigDict(from_attributes=True)

# 투자 지표 입력 구조 정의
class AnalysisCreate(BaseModel):
    ticker_symbol: str = Field(..., max_length=10)
    date: dt.date = Field(...)
    close_price: Optional[float] = Field(None, ge=0)

    ma5: Optional[float] = Field(None, ge=0)
    ma20: Optional[float] = Field(None, ge=0)
    ma60: Optional[float] = Field(None, ge=0)
    ma120: Optional[float] = Field(None, ge=0)
    
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    
    rsi: Optional[float] = Field(None, ge=0, le=100)
    
    bb_middle: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_lower: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


# 추천 입력 구조 정의
class RecommendationCreate(BaseModel):
    ticker_symbol: str = Field(..., max_length=10, description="종목 코드")
    analysis_id: str = Field(..., max_length=10, description="연관 분석 ID")
    signal_type: str = Field(..., max_length=10, description="신호 유형")
    strategy_name: str = Field(default='BASIC', max_length=50)
    base_date: dt.date = Field(..., description="추천 기준일")
    price: Optional[float] = Field(None, description="추천 당시 가격")
    is_sent: bool = Field(default=False)
    create_at: Optional[dt.datetime] = Field(default_factory=dt.datetime.now)

    model_config = ConfigDict(from_attributes=True)

# 포트폴리오 입력 구조 정의
class PortfolioCreate(BaseModel):
    ticker_symbol: str = Field(..., max_length=10)    
    recommendation_id: int = Field(...)
    quantity: Optional[int] = Field(None, description="보유 수량")
    buy_price: Optional[float] = Field(None, description="매수 단가")
    buy_date: Optional[dt.datetime] = None
    sell_price: Optional[float] = None
    sell_date: Optional[dt.datetime] = None
    is_active: int = Field(default=1)

    # SQLAlchemy 모델과의 호환성
    model_config = ConfigDict(from_attributes=True)

# 계좌 잔액 입력 구조 정의
class AccountHistoryCreate(BaseModel):
    portfolio_id: Optional[int] = Field(None, description="연관 포트폴리오 ID")
    transaction_type: str = Field(..., max_length=50, description="거래 유형")
    amount: float = Field(..., description="변동 금액")
    balance: float = Field(..., ge=0, description="최종 잔액")
    transaction_date: dt.datetime = Field(default_factory=dt.datetime.now)

    model_config = ConfigDict(from_attributes=True)


# 현금 입력 구조 정의
class CashInput(BaseModel):    
    amount: float
    transaction_type: str # 'DEPOSIT','WITHDRAWAL'

# 매매 입력 구조 정의
class TradeInput(BaseModel):
    ticker_symbol: str
    rec_id: int
    qty: int
    price: float
    transaction_type: str # 'BUY','SELL'