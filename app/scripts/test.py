from datetime import datetime,date
import pandas as pd

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

    # 12/26일 이후로 rec-buy 따져봐야돼
    analysis_with_id=fetch_analysis()
    print(f"analysis_with_id.head() = {analysis_with_id.head()}")
    print(f"analysis_with_id.tail() = {analysis_with_id.tail()}")

    rec =[]
    for __, analysis in analysis_with_id.iterrows():
        analysis_dict = analysis.to_dict()
        analysis_dict, buy_signal = validate_buy_strategy(analysis_dict)
        print(f"calculated for recommendation [{analysis_dict}]. result = [{buy_signal}]")

        if buy_signal ==True:
            print(f"analysis_dict = [{analysis_dict}]")
            rec.append(analysis_dict)

    rec_df = pd.DataFrame(rec)
    save_buy_rec(rec_df)

    # 루틴 4 : 디스코드 알림
    # print("루틴 4 : 추천사항을 디스코드 알림으로 전송합니다.")

    # send_recommendation_alerts()

    # 매수 조건 뜬 애들 데려다가(모두 샀다고 가정) 매도 조건 뜨는 지 비교
    


