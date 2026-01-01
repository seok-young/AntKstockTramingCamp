import pandas as pd


from app.service.database import SessionLocal,Base,engine
from app.model import Stock,ETF, Watchlist
from app.service.database import SessionLocal,Base,engine

'''
관심종목 데이터 로드 및 DB 저장
'''

def make_watchlist_df(Watchlist,asset_type):
    # watchlist_df 생성
    rows = []
    for stock_code in Watchlist:
        rows.append({
            'asset_type': asset_type,
            'ticker_symbol': stock_code
        })

    watchlist_df = pd.DataFrame(rows)
    return watchlist_df


def save_to_db_watchlist(watchlist_df):
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        # 주식
        for _, row in watchlist_df.iterrows():
            watchlist = Watchlist(
                asset_type=row['asset_type'],
                ticker_symbol=row['ticker_symbol'],
                is_watching=True,
                removed_at=None
            )
            session.add(watchlist)
        
        session.commit()
        print("Watchlist data saved to database successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error inserting data into database: {e}")
    finally:
        session.close()


