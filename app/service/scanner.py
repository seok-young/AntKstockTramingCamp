from app.core.database import SessionLocal, Base, engine
from app.model import Portfolio


""""
매수 대상
 - 계좌의 잔액 이하인 종목
 - 포트폴리오에 담겨있지 않은 종목
"""
def scan_buy():
    return None

"""
매도 대상
포트폴리오에 담겨있는 종목
"""
def scan_sell():
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
    


