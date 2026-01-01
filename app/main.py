from typing import Union
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.scripts.load_csv import load_csv_to_dataframe, preprocess_dataframe
from app.service.database import SessionLocal,Base,engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    
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