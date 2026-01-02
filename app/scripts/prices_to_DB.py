
import os
import sys
import glob
import pandas as pd


from app.core.database import SessionLocal,Base,engine

from app.service.collector import preprocess_price_df,save_price_to_db


# 폴더 내의 파일 리스트 만들기
def list_price_files(directory):
    target_dir = directory
    csv_path_list = glob.glob(os.path.join(target_dir,"*.csv"))      
    print(csv_path_list)

    return csv_path_list


# price_df 만들기
def price_csv_to_df(path):
    file_name = os.path.basename(path)
    stock_code = file_name.split('_')[1]
    try:
        price_df = pd.read_csv(path,encoding='cp949')
        price_df['stock_id'] = str(stock_code)
    except Exception as e:
        print(f"error_loading_CSV_file : {e}")
    return price_df


if __name__ == '__main__':

    BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
    )

    if BASE_DIR not in sys.path:
        sys.path.append(BASE_DIR)

    # 파일 경로 리스트에 담기
    print(f"BASE_DIR = {BASE_DIR}")    
    target = os.path.join(BASE_DIR,"price_data") # price_data 앞에 '/' 넣지 말 것 -> 넣으면 최상위 /price_data를 찾음
    print(f"target = {target}")

    path_list=list_price_files(target)
    
    # 데이터 불러와서 df로 담기
    prices_df_list = []

    for path in path_list:
        temp_df = price_csv_to_df(path)
        if temp_df.empty:
            continue

        prices_df_list.append(temp_df)

        print(f"df_length = {len(prices_df_list)}")
    
    if not prices_df_list:
        print("No Data From CSV")
    
    final_df = pd.concat(prices_df_list, ignore_index=True)
    print(f"df = {final_df.head(2)}, length = {len(final_df)}, df_columns = {final_df.columns.tolist()}")


    # 전처리하기
    preprocessed_df=preprocess_price_df(final_df)
    print(f"df = {preprocessed_df.head(2)}, length = {len(preprocessed_df)}, df_columns = {preprocessed_df.columns.tolist()}")

    # DB에 넣기
    save_price_to_db(preprocessed_df)
