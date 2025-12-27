from app.service.database import SessionLocal,Base,engine
from datetime import datetime
import pandas as pd


# DB에서 주가 불러오기
def get_price(stock_code):
    query = f"""
        SELECT date, close_price
        FROM daily_price
        WHERE stock_id = '{stock_code}'
        ORDER BY date ASC
    """
    df = pd.read_sql(query, con=engine)

    return df


# MA 계산 
def cal_MA(df):
    if df.empty:
        return df

    df['ma5'] = df['close_price'].rolling(window=5).mean()
    df['ma20'] = df['close_price'].rolling(window=20).mean()
    df['ma120'] = df['close_price'].rolling(window=120).mean()

    return df

# MACD 계산
def cal_MACD(df):
    if df.empty or len(df) < 26:
        return df
    
    ema12 = df['close_price'].ewm(span=12, adjust=False).mean()
    ema26 = df['close_price'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']

    return df

# RSI 계산
def cal_RSI_14(df, period=14):
    # 표준RSI(Wilder방식)을 사용

    if df.empty or len(df) <= period:
        return df
    
    delta = df['close_price'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

    rs = avg_gain/avg_loss
    df['rsi'] = 100 - (100/(1+rs))

    return df


# 볼린저 밴드 계산
def cal_Bollinger_band(df, window=20, num_std=2):
    if len(df) < window:
        return df
    
    df['bb_middle'] = df['close_price'].rolling(window=window).mean()

    std = df['close_price'].rolling(window=window).std()

    df['bb_upper'] = df['bb_middle'] + (std * num_std)
    df['bb_lower'] = df['bb_middle'] - (std * num_std)

    return df


# analysis 데이터 삽입


# 매수조건 비교

# 매도 조건 비교

# recommend 데이터 삽입