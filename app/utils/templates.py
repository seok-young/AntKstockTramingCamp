from datetime import date


def buy_message(symbol, price):
    today = date.today()
    return f"[{today}] 알림 \n- {symbol} 매수 조건 충족! \n- 현재가: {price}원"

def no_buy_message():
    today = date.today()
    return f"[{today}] 알림 \n- 매수 조건을 충족한 종목이 없습니다. "