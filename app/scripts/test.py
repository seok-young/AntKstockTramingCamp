from datetime import datetime,date
import pandas as pd
from sqlalchemy import desc


from app.service.analysis import (
    fetch_analysis,
)

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

from app.service.scanner import (
    get_current_holdings,
    get_watchlist,
    get_current_balance,
    get_buy_candidate,
    get_current_holdings

)

from app.model import (
    TradeInput,
    Analysis,
    Portfolio
)
from app.core.database import SessionLocal,Base,engine
from app.core.config import settings



if __name__ == '__main__':
    
    # session = SessionLocal()

    # # 매수 조건 뜬 애들 데려다가(모두 샀다고 가정) 매도 조건 뜨는 지 비교
    # # 가장 과거 rec 뜬 애들 7개 대상으로 매도 따져보자
    # query = f"""
    #     SELECT *
    #     FROM (
    #         SELECT *,
    #             ROW_NUMBER() OVER (PARTITION BY ticker_symbol ORDER BY base_date ASC) as row_num
    #         FROM recommendation
    #     ) as ranked_data
    #     WHERE row_num = 1
    #     ORDER BY base_date ASC
    #     LIMIT 7;
    # """
    
    # target = pd.read_sql(query, con=engine)
    # target['share'] = None
    # target['price'] = target['price'].astype(float)
    # # print(target.head())



    # """"
    # To-Do
    # 0. 몇 주를 사야되는 지 계산하기 V
    # 1. 포트폴리오에 저장하기       V
    # 2. account_history에 기록    V
    # 3. 매도 조건 따져보기
    # 4. 매도 API 테스트
    # """

    # # 1. 몇 주 사야 되는지 계산
    # target.loc[target['price'] >= 100000, 'share'] = 1
    # target.loc[target['price'] < 100000, 'share'] = 100000 // target['price']

    # # print(target.to_string())

    # # 2. 포폴 저장
    # manager = TradeManager(session)
    
    # cashinput = {
    #     'amount' : 1000000,
    #     'transaction_type' : 'DEPOSIT'
    # }

    # manager.record_cash_flow(cashinput)


    # temp =[]
    # for _,row in target.iterrows():
    #     trade = TradeInput(
    #         ticker_symbol=row['ticker_symbol'],
    #         rec_id=row['id'],
    #         qty=row['share'],
    #         price=row['price'],
    #         transaction_type=row['signal_type']
    #     )
    #     try :
    #         manager.execute_trade(trade)
    #     except Exception as e:
    #         print(f"Error during executing trade [{e}]")
    #     # print(trade)
   

    session = SessionLocal()
    manager = TradeManager(session)
    balance=manager.get_balance()
    buy_candidates = get_buy_candidate(balance)
    print(f"buy candidates = {buy_candidates}")

    analysis_list =[]
    for can in buy_candidates:
        analysis_obj = session.query(Analysis)\
            .filter(Analysis.ticker_symbol == can)\
            .order_by(desc(Analysis.date))\
            .first()
        
        analysis_dict = {c.name: getattr(analysis_obj, c.name) for c in analysis_obj.__table__.columns}
        analysis_list.append(analysis_dict)

    print(f"analysis dict = {analysis_list[0]}")
    print(f"analysis_list length = {len(analysis_list)}")

    # 루틴 7 : 매수 조건 따지기
    rec_buy = []
    for analysis in analysis_list:
        analysis_dict, buy_sign = validate_buy_strategy(analysis)

        if buy_sign == True:
            print(f"buy_signal is True for [{analysis_dict}]")
            rec_buy.append(analysis_dict)
    
    rec_df = pd.DataFrame(rec_buy)
    save_buy_rec(rec_df)
    
  