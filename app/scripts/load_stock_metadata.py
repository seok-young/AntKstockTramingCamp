# scripts/load_stock_metadata.py

import os
import sys

# 프로젝트 경로 추가 (scripts 폴더에서 app 폴더 import 가능하게)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.service.load_csv import (
    load_csv_to_dataframe,
    preprocess_dataframe,
    save_to_db
)

FILE_PATH = "/code/app/data_0233_20251108.csv"


def main():
    print("CSV 로드 중...")
    df = load_csv_to_dataframe(FILE_PATH)

    if df is None:
        print("CSV 로드 실패")
        return

    print("전처리 중...")
    df = preprocess_dataframe(df)

    print("DB 저장 중...")
    save_to_db(df)

    print("작업 완료!")


if __name__ == "__main__":
    main()
