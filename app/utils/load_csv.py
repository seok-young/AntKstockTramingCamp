import pandas as pd
from sqlalchemy import create_engine
import os

from app.core.config import settings

def load_csv_to_dataframe(file_path):
    try:
        df = pd.read_csv(file_path,encoding='cp949')
        return df
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None
    

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
        "date_listing", "market_type",
        "stock_class", "par_value", "shares_listed"
    ]
    df = df[final_columns]
    # df = df.dropna()
    return df