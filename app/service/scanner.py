from app.core.database import SessionLocal, Base, engine
from app.model import Portfolio, Watchlist,AccountHistory,DailyPrice

from sqlalchemy import desc
import numpy as np

def get_watchlist():
    session = SessionLocal()
    try:
        result = session.query(Watchlist.ticker_symbol)\
                        .filter(Watchlist.is_watching == 1)\
                        .all()        
        return [r[0] for r in result]
    finally:
        session.close()



    
def get_current_balance():
    session = SessionLocal()
    try:
        result = session.query(AccountHistory.balance)\
                        .order_by(desc(AccountHistory.transaction_date), desc(AccountHistory.id))\
                        .first()
        return result[0]
    except Exception as e:
        print(f"Error during getting current balance [{e}]")
    finally:
        session.close()
    
def get_latest_price(ticker_symbol):
    session = SessionLocal()
    try:
        result = session.query(DailyPrice.close_price)\
                        .filter(DailyPrice.ticker_symbol == ticker_symbol)\
                        .order_by(desc(DailyPrice.date))\
                        .first()
        return np.abs(result[0])
    except Exception as e:
        print(f"Error during getting price for buy candidate {e}")
    finally:
        session.close()
    return None



"""
매도 대상
포트폴리오에 담겨있는 종목

-> get_current_holdings() 쓰면 됨
"""
def get_current_holdings():
    session = SessionLocal()
    try:
        result = session.query(Portfolio.ticker_symbol)\
                        .filter(Portfolio.is_active == 1)\
                        .all()        
        return [r[0] for r in result]
    except Exception as e:
        print(f"Error during scanning sell [{e}]")
        return None    
    finally:
        session.close()



""""
매수 대상
 - 포트폴리오에 담겨있지 않은 종목
 - 가상정산 후 잔액 혹은 계좌의 잔액 이하인 종목
"""
def get_buy_candidate(balance):
    watchlist = set(get_watchlist())
    holdings = set(get_current_holdings())
    # balance = get_current_balance()

    # 포트폴리오에 담겨있지 않은 종목
    candidate = watchlist - holdings

    final_candidate=[]
    # 계좌의 잔액 이하인 종목
    for can in candidate:
        price = get_latest_price(can)
        if price <= balance:
            final_candidate.append(can)
            
    return final_candidate