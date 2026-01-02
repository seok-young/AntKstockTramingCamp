
import json
from datetime import datetime, timedelta
import time
import pandas as pd
import os

from app.core.config import settings
from app.core.database import SessionLocal,Base,engine

from app.service.collector import fn_au10001, fn_ka10086,get_interest_stocksID


def collect_12months_data(token, stk_cd):
    print("ENTER collect_12months_data")
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)

    all_data = []
    current_date = end_date

    while current_date >= start_date:
        qry_dt = current_date.strftime('%Y%m%d')
        cont_yn = 'N'  # 해당 날짜 조회의 시작은 항상 'N'
        next_key = ''
        
        print(f"--- Fetching data for date: {qry_dt} ---")
        
        
        params = {
            'stk_cd': stk_cd,
            'qry_dt': qry_dt,
            'indc_tp': '0',
        }
        
  
        res_json, cont_yn_res, next_key_res = fn_ka10086(token, params, cont_yn, next_key)
        
        if res_json is None:
            break

        daily = res_json.get('daly_stkpc', [])
        if not daily:
            break

        all_data.extend(daily)
        print(f"Collected {len(daily)} rows. current_date {current_date} Next key: {next_key_res}")


        # 연속 데이터가 있는지 확인
        if cont_yn_res == 'Y' and next_key_res:
            cont_yn = 'Y' # 다음 요청을 위해 업데이트
            next_key = next_key_res
            time.sleep(0.25) # 과도한 호출 방지
        else:
            break # 더 이상 데이터가 없으면 내부 루프 종료
        
       
        current_date -= timedelta(days=20)
        
    return all_data




if __name__ == '__main__':

    params_token = {
		'grant_type': 'client_credentials',  
		'appkey': settings.APP_KEY,
		'secretkey': settings.SECRET_KEY
	}
    ACCESS_TOKEN = fn_au10001(params_token)

    # 종목코드 설정
    stockID_list=get_interest_stocksID()
    for stockID in stockID_list:
        STOCK_CODE = stockID  # 예: 삼성전자

        prices = collect_12months_data(ACCESS_TOKEN, STOCK_CODE)

        if prices:
            prices_df = pd.DataFrame(prices)
            if 'date' in prices_df.columns:
                prices_df= prices_df.drop_duplicates(subset='date', keep='first')
                prices_df = prices_df.sort_values(by='date').reset_index(drop=True)

        save_path = '/code/app/price_data'
        if not os.path.exists(save_path):
            os.makedirs(save_path)


        save_path = f'{save_path}/data_{STOCK_CODE}_{datetime.now().strftime("%Y%m%d")}.csv'
        prices_df.to_csv(save_path, index=False)
        print(f"✅ 파일 저장 완료: {os.path.abspath(save_path)}")
    
        time.sleep(0.5)
