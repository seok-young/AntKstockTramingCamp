from app.core.database import SessionLocal, Base, engine

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
#     session = SessionLocal()
#     query = f"""
#     SELECT ticker_symbol FROM portfolio 
#     WHERE      

# """
    return None


