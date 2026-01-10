from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from datetime import datetime, time, timedelta
import pandas as pd

from app.scripts.load_csv import load_csv_to_dataframe, preprocess_dataframe
from app.core.database import SessionLocal,Base,engine
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
    save_buy_rec,
    validate_buy_strategy
)

from app.service.notify import send_recommendation_alerts

"""
to-do
루틴 초반에 에러나면 뒤에 거 실행하지 말고 알림
"""

def daily_stock_routine():
    print(f"[{datetime.now()}] 루틴 실행 시작")
    
    # 루틴 1 : 주가 수집 API
    stock_list = get_interest_stocksID()
    total_df_list =[]

    print(f"루틴 1 : 데이터를 수집합니다.")
    for stock in stock_list:
        ticker_symbol, result_json = fetch_daily_prices(stock)
        result_df = preprocess_prices(ticker_symbol,result_json)
        save_price_to_db(result_df)
        # print(result_df.head())


    # 루틴 2 : 분석 및 저장
    print("루틴 2 : 지표 계산을 시작합니다.")

    df_with_id=fetch_analysis()

    # 루틴 3 : 추천 및 저장
    print("루틴 3 : 추천을 위한 조건을 비교합니다.")

    rec =[]
    for __, analysis in df_with_id.iterrows():
        analysis_dict = analysis.to_dict()
        analysis_dict, buy_signal = validate_buy_strategy(analysis_dict)
        print(f"calculated for recommendation [{analysis_dict}]. result = [{buy_signal}]")

        if buy_signal ==True:
            print(f"analysis_dict = [{analysis_dict}]")
            rec.append(analysis_dict)

        rec_df = pd.DataFrame(rec)
        save_buy_rec(rec_df)

    # 루틴 4 : 디스코드 알림
    print("루틴 4 : 추천사항을 디스코드 알림으로 전송합니다.")

    send_recommendation_alerts()

    print(f"[{datetime.now()}] 루틴 실행 완료")

@asynccontextmanager
async def lifespan(app: FastAPI):  
    # yield 이전 : 애플리케이션이 요청을 받기 시작하기 전, 시작 동안에 실행
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")

    # 정기 스케줄
    scheduler.add_job(
        daily_stock_routine,
        'cron',
        day_of_week='mon-sun',
        hour=14,
        minute=1,
        id="daily_routine"
    )
        # 'cron' : run the job periodically certain time(s) of day

    # 18시 이후에 서버를 켰을 때 대비
    now = datetime.now()
    current_time = now.time()
    start_window = time(18,0)  # 오후 6시
    end_window = time(20,0)    # 오후 8시

    if (now.weekday() < 5) and (start_window <= current_time <= end_window):
        print("서버 시작 시점이 정기 예약 시간이후입니다. 5초 뒤 예약 작업을 시작합니다.")
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