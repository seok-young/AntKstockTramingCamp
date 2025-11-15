from typing import Union
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.utils.load_csv import load_csv_to_dataframe, preprocess_dataframe
from app.database import SessionLocal,Base,engine
from app.model import Stock

@asynccontextmanager
async def lifespan(app: FastAPI):
    # print("현재 작업 디렉토리:", os.getcwd())
    BASE_DIR=os.path.dirname(os.path.abspath(__file__))
    CSV_PATH=os.path.join(BASE_DIR, "data_0233_20251108.csv")
    df = load_csv_to_dataframe(CSV_PATH)
    print("전처리 전 df : " ,df.head())
    df = preprocess_dataframe(df)
    df['par_value'] = df['par_value'].apply(Stock.parse_par_value)
    print("전처리된 데이터프레임 : " ,df.head())
    if df is not None:
        print("CSV file loaded successfully:")
        print(df.head())
    else:
        print("Failed to load CSV file.")
    # Base.metadata.create_all(bind=engine)
    # session = SessionLocal()
    # try:
    #     for _, row in df.iterrows():
    #         stock = Stock(
    #             symbol_origin=row['symbol_origin'],
    #             symbol=row['symbol'],
    #             name_kor=row['name_kor'],
    #             date_listing=row['date_listing'],
    #             market_type=row['market_type'],
    #             stock_class=row['stock_class'],
    #             par_value=row['par_value'],
    #             shares_listed=row['shares_listed']
    #         )
    #         session.add(stock)
    #     session.commit()
    # except Exception as e:
    #     session.rollback()
    #     print(f"Error inserting data into database: {e}")
    # finally:
    #     session.close()

    
    # yield 이전 : 애플리케이션이 요청을 받기 시작하기 전, 시작 동안에 실행
    yield
    #  yield 이후 : 애플리케이션이 요청 처리 완료 후, 종료 직전에 실행
app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}