# scripts/load_stock_metadata.py

import os
import sys
import pandas as pd

from app.scripts.load_csv import (
    load_csv_to_dataframe,
    preprocess_dataframe,
    preprocess_dataframe_ETF,
    save_to_db,
    save_to_db_etf
)

from app.scripts.load_watchlist import (
    make_watchlist_df,
    save_to_db_watchlist
)

from app.service.notify import send_recommendation_alerts


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

FILE_PATH = os.path.join(BASE_DIR, "data_0233_20251108.csv")
FILE_PATH_ETF = os.path.join(BASE_DIR, "etf_data_1606_20251123.csv")


def main():
    '''
    stock, etf 데이터 로드 및 DB 저장
    '''
    # print("CSV 로드 중...")
    # df = load_csv_to_dataframe(FILE_PATH)
    # df_etf = load_csv_to_dataframe(FILE_PATH_ETF)

    # if df_etf is None:
    #     print("CSV 로드 실패")
    #     return

    # print(df.head().to_string())
    # print("전처리 중...")
    # df = preprocess_dataframe(df)
    # df_etf = preprocess_dataframe_ETF(df_etf)
  
    # print("DB 저장 중...")
    # save_to_db_etf(df_etf)
    # save_to_db(df)
    # print("작업 완료!")

    # '''
    # watchlist 데이터 로드 및 DB 저장
    # '''
    # Watchlist_stock =['005930','000660','034730','001500','000270','035420','035720','207940','066570','005490',
    #                 '006400','051910','012330','009540','018880','105560','055550','086790','032830','034220',
    #                 '009150','009830','051900','096770','086280','010950','097950','090430','033780','011170',
    #                 '323410','247540','112040','377300','035760','086520','196170','263750','011200','357780'
    #                 ]
    # Watchlist_etf =['069500','102110','229200','143860','091160','091170','228800','469790','360750','132030',
    #                 ]
    # watchlist_df = make_watchlist_df(Watchlist_stock,'Stock')
    # save_to_db_watchlist(watchlist_df)
    # watchlist_df_etf = make_watchlist_df(Watchlist_etf,'ETF')
    # save_to_db_watchlist(watchlist_df_etf)

    send_recommendation_alerts()
    

if __name__ == "__main__":
    main()
