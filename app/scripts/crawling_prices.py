import requests
import json
from datetime import datetime, timedelta
import time
import pandas as pd
import os

from app.core.config import settings


# 접근토큰 발급
def fn_au10001(data):
	# 1. 요청할 API URL
	host = 'https://api.kiwoom.com' # 실전투자
	endpoint = '/oauth2/token'
	url =  host + endpoint

	# 2. header 데이터
	headers = {
		'Content-Type': 'application/json;charset=UTF-8', # 컨텐츠타입
	}

	# 3. http POST 요청
	response = requests.post(url, headers=headers, json=data, timeout=10)
	
	if response.status_code == 200:
		access_token = response.json().get('token')
		return access_token
	else:
		print('error:', response.status_code)

def fn_ka10086(token, data, cont_yn='N', next_key=''):
    host = 'https://api.kiwoom.com'  # 실전투자
    endpoint = '/api/dostk/mrkcond'
    url = host + endpoint

    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'authorization': f'Bearer {token}',
        'cont-yn': cont_yn,
        'next-key': next_key,
        'api-id': 'ka10086',
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return None, None, None

        res_json = response.json()
        cont_yn_res = response.headers.get('cont-yn', 'N')
        next_key_res = response.headers.get('next-key', '')
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT 발생")  

    return res_json, cont_yn_res, next_key_res


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
        
        # fn_ka10086 내부에서 headers에 cont_yn과 next_key를 잘 넣고 있는지 확인하세요.
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
        
        # 날짜를 20일 전으로 이동 (중복 데이터가 발생할 수 있으므로 나중에 pandas로 drop_duplicates 권장)
        current_date -= timedelta(days=20)
        
    return all_data

if __name__ == '__main__':

    params_token = {
		'grant_type': 'client_credentials',  
		'appkey': settings.APP_KEY,
		'secretkey': settings.SECRET_KEY
	}
    ACCESS_TOKEN = fn_au10001(params_token)
    STOCK_CODE = '005930'  # 예: 삼성전자

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
