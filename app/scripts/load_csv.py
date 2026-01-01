import pandas as pd
from sqlalchemy import create_engine
import os
import traceback

from app.core.config import settings
from app.model import Ticker
from app.service.database import SessionLocal,Base,engine

def load_csv_to_dataframe(file_path):
    try:
        df = pd.read_csv(file_path,encoding='cp949')
        return df
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None

def save_to_db(df):
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        for _, row in df.iterrows():
            ticker_stock = Ticker(
                symbol_origin=row['symbol_origin'],
                symbol=row['symbol'],
                name_kor=row['name_kor'],                
                asset_type = 'Stock',
                market_type=row['market_type'],
                date_listing=row['date_listing'],
                total_shares=row['shares_listed'],
            )
            session.add(ticker_stock)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error inserting data into database: {e}")
        traceback.print_exc()
    finally:
        session.close()


def save_to_db_etf(df):
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        for _, row in df.iterrows():
            ticker_etf = Ticker(
                symbol_origin=row['symbol_origin'],
                symbol=row['symbol'],
                name_kor=row['name_kor'],
                asset_type = 'ETF',
                market_type=row['base_market_type'],
                date_listing=row['date_listing'],                
                total_shares=row['shares_outstanding'],
            )
            session.add(ticker_etf)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error inserting data into database: {e}")
        traceback.print_exc()
    finally:
        session.close()

def preprocess_dataframe(df):
    original_cols = [
        '표준코드','단축코드','한글 종목명','한글 종목약명',
        '영문 종목명','상장일','시장구분','증권구분',
        '소속부','주식종류','액면가','상장주식수'
    ]

    new_cols = [
        'symbol_origin','symbol','name_kor','name_kor_short',
        'name_eng','date_listing','market_type','security_type',
        'section','stock_class','par_value','shares_listed'
    ]

    df=pd.DataFrame(df,columns=original_cols)
    df.columns = new_cols
    final_columns = [
        "symbol_origin", "symbol","name_kor",
        "market_type","date_listing","shares_listed"
    ]
    df = df[final_columns]
    # df = df.dropna()
    return df

def preprocess_dataframe_ETF(df):
    original_cols = [
        '표준코드','단축코드','한글종목명','한글종목약명',
        '영문종목명','상장일','기초지수명','지수산출기관',
        '추적배수','복제방법','기초시장분류','기초자산분류',
        '상장좌수','운용사','CU수량','총보수','과세유형'
    ]

    new_cols = [
        'symbol_origin', 'symbol','name_kor','short_name_kor',
        'name_en','date_listing', 'base_index_name','index_provider',
        'leverage_type','replication_method','base_market_type','base_asset_type',
        'shares_outstanding','asset_manager', 'creation_unit', 'expense_ratio', 'tax_type'
    ]
    df.columns = new_cols
    final_columns = [
        'symbol_origin', 'symbol','name_kor',
        "date_listing",'base_market_type','base_asset_type',
        'shares_outstanding', 
    ]

    df=df[final_columns]
    return df