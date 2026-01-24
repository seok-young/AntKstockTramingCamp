from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from datetime import datetime, date, time, timedelta
import pandas as pd
from sqlalchemy import desc

from app.scripts.load_csv import load_csv_to_dataframe, preprocess_dataframe
from app.core.database import SessionLocal,Base,engine
from app.model import (
    Analysis,
    Portfolio,
    TradeInput
)
from app.service.collector import(
    get_latest_date,
    get_interest_stocksID,
    fetch_daily_prices,
    preprocess_prices,
    save_price_to_db,
)

from app.service.analysis import (
    fetch_analysis
)

from app.service.recommend import (
    validate_sell_strategy,
    save_buy_rec,
    save_sell_rec,
    validate_buy_strategy
)

from app.service.notify import send_recommendation_alerts

from app.service.scanner import (
    get_current_holdings, 
    get_current_balance,
    get_buy_candidate
)

from app.service.trade_manager import TradeManager

"""
to-do
루틴 초반에 에러나면 뒤에 거 실행하지 말고 알림

데일리 루틴
0. 데이터 수집 V
1. 매도 후보 정하기 V
2. 매도 후보 자격 검증 V
3. 가상정산 V
4. 매수 후보 정하기
5. 매수 후보 자격 검증
6. 통합(매수 + 매도) 알림 정산
"""

def daily_stock_routine():
    pd.set_option('display.max_columns', None)
    session = SessionLocal()
    print(f"[{datetime.now()}] 루틴 실행 시작")
    
    # 루틴 1 : 주가 수집 API
    stock_list = get_interest_stocksID()
    total_df_list =[]

    print(f"데이터를 수집합니다.")
    for stock in stock_list:
        ticker_symbol, result_json = fetch_daily_prices(stock)
        result_df = preprocess_prices(ticker_symbol,result_json)
        save_price_to_db(result_df)
        # print(result_df.head())


    # 루틴 2 : 분석 및 저장
    df_with_id=fetch_analysis()

    #--------------------------------------------------------------------#
    
    # 루틴 3 : 매도 후보 불러오기
    sell_candidates=get_current_holdings()
    
    rec_sell =[]
    portfolio_list =[]

    work_queue = []
    for can in sell_candidates:
        
        analysis_res=session.query(Analysis)\
            .filter(Analysis.ticker_symbol == can)\
            .order_by(desc(Analysis.date))\
            .limit(2)\
            .all()

        portfolio_obj=session.query(Portfolio)\
            .filter(Portfolio.ticker_symbol == can)\
            .first()
        
        if (len(analysis_res) >= 2) and (portfolio_obj) :
            analysis_today = analysis_res[0]
            analysis_yes = analysis_res[1]     
            
            # dict로 변환
            analysis_today_dict = {c.name: getattr(analysis_today, c.name) for c in analysis_today.__table__.columns}
            analysis_yes_dict = {c.name: getattr(analysis_yes, c.name) for c in analysis_yes.__table__.columns}
            portfolio_dict = {c.name: getattr(portfolio_obj, c.name) for c in portfolio_obj.__table__.columns}

            work_queue.append({
                'today':analysis_today_dict,
                'yesterday':analysis_yes_dict,
                'portfolio':portfolio_dict                
            })
            print(f"work_queue length : {len(work_queue)}")
            print(f"work_queue : {work_queue[0]}")
        else:
            print("Not Enough Analysis Data For Sell_recommendation")



    # 루틴 4 : 매도 조건 따져보기(매도 조건 수정하기!!!)
    rec_sell =[]
    portfolio_list =[]    
    for work in  work_queue:
        analysis_dict, sell_signal = validate_sell_strategy(work['today'], work['yesterday'], work['portfolio'])
        if sell_signal ==True:
            rec_sell.append(analysis_dict)
            portfolio_list.append(work['portfolio'])

    rec_df = pd.DataFrame(rec_sell)
    port_df = pd.DataFrame(portfolio_list)
        
    # 루틴 5 : 가상 정산
    # 매도 추천이 있을때만
    manager = TradeManager(session)
    if not rec_df.empty:
        print(f"DEBUG: rec_df columns -> {rec_df.columns.tolist()}")
        print(f"DEBUG: port_df columns -> {port_df.columns.tolist()}")
        save_sell_rec(rec_df)    

        # 가상의 trade_date 만들기
        
        virtual_balance = get_current_balance() 
        merged_df = rec_df.merge(port_df, on = 'ticker_symbol', how='left', suffixes=('_rec','_port'))
        print(merged_df.head())
        for index, row in merged_df.iterrows():
            temp_trade = TradeInput(
                ticker_symbol = row['ticker_symbol'],
                rec_id = row['id_rec'],                 # recommendation.id
                qty = row['quantity'],                  # portfolio.quantity
                price = row['price'],                   # recommendation.price
                transaction_type= 'SELL',
            )
            virtual_balance = manager.calculate_virtual_balance(virtual_balance, temp_trade)
        

    else:
        virtual_balance = manager.get_balance()
        print("There is No Sell Recommendation Today")

    print(f"virtual_balance = {virtual_balance}")
    # 루틴 6 : 매수 후보 정하기 
    buy_candidates = get_buy_candidate(virtual_balance)

    # 루틴 7 : 매수 조건 따지기


    # rec_buy =[]
    # for __, analysis in df_with_id.iterrows():
    #     analysis_dict = analysis.to_dict()
    #     analysis_dict, buy_signal = validate_buy_strategy(analysis_dict)
    #     print(f"calculated for recommendation [{analysis_dict}]. result = [{buy_signal}]")

    #     if buy_signal ==True:
    #         print(f"analysis_dict = [{analysis_dict}]")
    #         rec_buy.append(analysis_dict)

    #     rec_df = pd.DataFrame(rec_buy)
    #     save_buy_rec(rec_df)

    # # 루틴 4 : 디스코드 알림
    # print("루틴 4 : 추천사항을 디스코드 알림으로 전송합니다.")

    # send_recommendation_alerts()

    # print(f"[{datetime.now()}] 루틴 실행 완료")

@asynccontextmanager
async def lifespan(app: FastAPI):  
    # yield 이전 : 애플리케이션이 요청을 받기 시작하기 전, 시작 동안에 실행
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")

    # 정기 스케줄
    scheduler.add_job(
        daily_stock_routine,
        'cron',
        day_of_week='mon-sun',
        hour=12,
        minute=23,
        id="daily_routine"
    )
        # 'cron' : run the job periodically certain time(s) of day

    # 18시 이후에 서버를 켰을 때 대비
    now = datetime.now()
    current_time = now.time()
    start_window = time(18,0)  # 오후 6시
    end_window = time(20,0)    # 오후 8시

    if (now.weekday() < 5) and (start_window <= current_time <= end_window):
        print("정기예약시간 이후에 서버를 시작했습니다. 5초 뒤 예약 작업을 시작합니다.")
        run_at = now + timedelta(seconds=5)
        scheduler.add_job(
            daily_stock_routine,
            'date',
            run_date=run_at,
            id="immediate_run"
        )
        # 'date' : run the job just once at certain point of time
    else:
        print("정규 실행 시간 시간대가 아니므로 예약된 스케줄에 따라 실행됩니다.")
        
    
    scheduler.start()
    print("APScheduler 시작")
    for job in scheduler.get_jobs():
        print(f"Job ID: {job.id}, Next Run: {job.next_run_time}")
    yield
    #  yield 이후 : 애플리케이션이 요청 처리 완료 후, 종료 직전에 실행
    scheduler.shutdown()
app = FastAPI(lifespan=lifespan)