import pandas as pd
import numpy as np
import datetime as dt

from app.core.database import SessionLocal,Base,engine
from app.model import Analysis, Watchlist


# 관심 종목 리스트 불러오기
def get_target_stocksList():

    session=SessionLocal()
    try:
        watchlist_stocks = session.query(Watchlist.asset_id).filter(Watchlist.is_watching == 1).all()
        if not watchlist_stocks:
            print("No Watchlist from DB")
            return []
        
        target_list = [s[0] for s in watchlist_stocks]
        return target_list
    except Exception as e:
        print(f"Error occurred in get_target_stocksList: {e}")
        return []
    finally: 
        session.close()
    


# 처음 DB에서 주가 불러오기
def get_price(stock_code):
    # daily_price 테이블의 close_price의 절댓값을 불러옴
    query = f"""
        SELECT stock_id, date, ABS(close_price) as close_price
        FROM daily_price
        WHERE stock_id = '{stock_code}'
        ORDER BY date ASC
    """
    df = pd.read_sql(query, con=engine)

    return df

# 주가 불러오기
"""
    TO-DO
    analysis 테이블에서 가장 최신 데이터를 확인하고 
    그 이후의 데이터만 수집하도록 필터링해서 조회
"""

# MA 계산 
def cal_MA(df):
    if df.empty:
        return df

    df['ma5'] = df['close_price'].rolling(window=5).mean()
    df['ma20'] = df['close_price'].rolling(window=20).mean()
    df['ma60'] = df['close_price'].rolling(window=60).mean()
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


# 처음 analysis 데이터 삽입
"""
    analysis 테이블 생성 및
    초기 데이터 입력
"""
def save_analysis_to_DB(df):
    # nan -> None
    final_df = df.copy()
    final_df = final_df.replace({np.nan:None})

    # Base.metadata.create_all(bind=engine)
    session=SessionLocal()
    try:
        data_list = final_df.to_dict(orient='records')
        session.bulk_insert_mappings(Analysis, data_list)
        session.commit()
        print("Success Uploading analysis_df to DB")
    except Exception as e:
        session.rollback()
        print(f"Error : {e}")
    finally:
        session.close()
    return

# analysis 데이터 삽입
"""
    TO-DO
    원래 있는 analysis 테이블에 
    가장 최신 데이터 이후의 데이터만 필터링하여 추가로 입력
"""



