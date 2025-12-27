
import os
import sys
import glob
import pandas as pd
from datetime import datetime

from app.service.database import SessionLocal,Base,engine
from app.model import DailyPrice as daily_price
# from app.scripts.load_csv import load_csv_to_dataframe



# 폴더 내의 파일 리스트 만들기
def list_price_files(directory):
    target_dir = directory
    csv_path_list = glob.glob(os.path.join(target_dir,"*.csv"))      
    print(csv_path_list)

    return csv_path_list

"""
    TO-DO : API 호출하여 자동으로 수집하는 로직
"""

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



# 전처리
def preprocess_price_df(df):
    """
    * row data columns
    date,open_pric,high_pric,low_pric,close_pric,pred_rt,flu_rt,trde_qty,amt_mn,crd_rt,ind,orgn,for_qty,frgn,prm,for_rt,for_poss,for_wght,for_netprps,orgn_netprps,ind_netprps,crd_remn_rt

    
    * daliy_price columns(after preprocessing)
    id,stock_id,date,open_price,high_price,low_price,close_price,trde_qty,created_at,updated_at
    """
    if df.empty:
        print("No df for preprocessing")
        return df

    rename_map ={
        "open_pric":"open_price",
        "high_pric":"high_price",
        "low_pric":"low_price",
        "close_pric":"close_price",
    }
    df = df.rename(columns = rename_map)

    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    now = datetime.now()
    df['created_at'] = now
    df['updated_at'] = now

    final_columns = [
        "stock_id","date","open_price","high_price","low_price","close_price",
        "trde_qty","created_at","updated_at"
    ]
    
    return df[final_columns]

# DB 삽입
def save_price_to_db(df):
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        data_list = df.to_dict(orient='records')
        session.bulk_insert_mappings(daily_price,data_list)
        session.commit()
        print("Success Uploading price_df to DB")
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

    return




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
