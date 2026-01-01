from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from datetime import datetime, time, timedelta

from app.scripts.load_csv import load_csv_to_dataframe, preprocess_dataframe
from app.service.database import SessionLocal,Base,engine

def daily_stock_routine():
    print(f"[{datetime.now()}] 루틴 실행 시작")
    # 주가 수집 API
    # 분석 - 추천
    # 디스코드 알림
    print(f"[{datetime.now()}] 루틴 실행 완료")

@asynccontextmanager
async def lifespan(app: FastAPI):  
    # yield 이전 : 애플리케이션이 요청을 받기 시작하기 전, 시작 동안에 실행
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")

    # 정기 스케줄
    scheduler.add_job(
        daily_stock_routine,
        'cron',
        day_of_week='mon-fri',
        hour=15,
        minute=30,
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