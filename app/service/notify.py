import requests

from app.core.config import settings
from app.service.database import SessionLocal,Base,engine
from app.model import Recommendation
from app.utils.templates import buy_message, no_buy_message

def send_recommendation_alerts():
    session = SessionLocal()
    try:
        unsent_items = session.query(Recommendation).filter(Recommendation.is_sent == 0).all()

        if not unsent_items:
            no_buy_message()
            return
        for item in unsent_items:
            if item.signal_type == "BUY":
                symbol = item.ticker_symbol
                price = item.price
                message = buy_message(symbol, price)
                response = requests.post(settings.WEBHOOK_URL, json={"content": message})

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