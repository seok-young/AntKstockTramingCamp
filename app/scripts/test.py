from datetime import datetime,date
from app.service.analysis import (
    fetch_analysis,
)
from app.core.database import Base,engine

from app.service.recommend import (
    get_recent_analysis,
    validate_buy_strategy,
    save_buy_rec
)

from app.service.notify import send_recommendation_alerts

from app.service.collector import (
    get_latest_date,
    get_interest_stocksID,
    fetch_daily_prices,
    preprocess_prices,
    save_price_to_db
    )

from app.service.trade_manager import (
    TradeManager
)

from app.core.database import SessionLocal,Base,engine
from app.core.config import settings



if __name__ == '__main__':
    
    session = SessionLocal()
    manager = TradeManager(session)
    # deposit_data = {
    #     'transaction_type' : 'DEPOSIT',
    #     'amount' : 1000000
    # }

    # manager.record_cash_flow(deposit_data)

    # 매수 조건 뜬 애들 데려다가(모두 샀다고 가정) 매도 조건 뜨는 지 비교
    fetch_analysis()


