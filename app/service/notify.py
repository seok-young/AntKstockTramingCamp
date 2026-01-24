import requests
import time

from app.core.config import settings
from app.core.database import SessionLocal,Base,engine
from app.model import Recommendation
from app.utils.templates import (
    buy_message,
    no_buy_message,
    sell_message,
    no_sell_message,
)
def send_recommendation_alerts():
    session = SessionLocal()
    try:
        buy_unsent_items = session.query(Recommendation)\
            .filter(Recommendation.is_sent == 0)\
            .filter(Recommendation.signal_type == 'BUY')\
            .all()
        
        sell_unsent_items = session.query(Recommendation)\
            .filter(Recommendation.is_sent == 0)\
            .filter(Recommendation.signal_type == 'SELL')\
            .all()

        if not buy_unsent_items:
            message = no_buy_message()
            response = requests.post(settings.WEBHOOK_URL, json={"content": message})
            
        if not sell_unsent_items:
            message = no_sell_message()
            response = requests.post(settings.WEBHOOK_URL, json={"content": message})
             

        for item in buy_unsent_items:
            if item.signal_type == "BUY":
                symbol = item.ticker_symbol
                price = item.price
                message = buy_message(symbol, price)
                response = requests.post(settings.WEBHOOK_URL, json={"content": message})
                time.sleep(1)

                # 디스코드 성공 응답 : 204
                if response.status_code == 204:
                    item.is_sent = 1
                    print(f"{item.ticker_symbol} - {item.signal_type} 알림 전송 완료")

                else:
                    print(f"전송실패 : {item.ticker_symbol} / {response.status_code}")

        for item in sell_unsent_items:
            if item.signal_type == "SELL":
                symbol = item.ticker_symbol
                price = item.price
                message = sell_message(symbol, price)
                response = requests.post(settings.WEBHOOK_URL, json={"content": message})
                time.sleep(1)

                # 디스코드 성공 응답 : 204
                if response.status_code == 204:
                    item.is_sent = 1
                    print(f"{item.ticker_symbol} - {item.signal_type} 알림 전송 완료")

                else:
                    print(f"전송실패 : {item.ticker_symbol} / {response.status_code}")

        session.commit()

    except Exception as e:
        print(f"Error during sending notification Message : {e}")
    return False