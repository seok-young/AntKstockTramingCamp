import requests
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import desc, text
import time

from app.core.database import SessionLocal,Base,engine
from app.model import Watchlist as watchlist
from app.model import DailyPrice as daily_price
from app.core.config import settings
"""
TO-DO

 - DB에서 제일 최신의 날짜 확인하고 그 이후의 데이터 수집 
 - 불러온 주가 데이터 -> df로

"""

# 관심 종목 DB 조회 -> 리스트
def get_interest_stocksID():
    session = SessionLocal()
    try:
        asset_ids = session.query(watchlist.ticker_symbol).filter(watchlist.is_watching == True).all()
        asset_id_list = [row[0] for row in asset_ids]
        return asset_id_list
    except Exception as e:
        print("DB 조회 중 오류 발생:", e)
        return []
    finally:
        session.close()

# DB 최신 날짜 확인하기
def get_latest_date(target_ticker):
    session = SessionLocal()
    try:
        result = session.query(daily_price.date)\
        .filter(daily_price.ticker_symbol == target_ticker)\
        .order_by(desc(daily_price.date))\
        .first()

        return result[0] if result else None
        # result[0] = 2025-12-24, type = <class 'datetime.date'>
    except Exception as e:
        return None
    finally:
        session.close()



# 접근토큰 발급
def fn_au10001(grant_type='client_credentials', appkey=settings.APP_KEY, secretkey=settings.SECRET_KEY):
	# 1. 요청할 API URL
	host = 'https://api.kiwoom.com' # 실전투자
	endpoint = '/oauth2/token'
	url =  host + endpoint

	# 2. header 데이터
	headers = {
	    'Content-Type': 'application/json;charset=UTF-8', # 컨텐츠타입
	}

	data = {
        "grant_type": grant_type,
        "appkey": appkey,
        "secretkey": secretkey
    }

	# 3. http POST 요청
	response = requests.post(url, headers=headers, json=data, timeout=10)
	
	if response.status_code == 200:
		access_token = response.json().get('token')
		return access_token
	else:
		print('error:', response.status_code)
		
# 주가 수집
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





# 전처리(json -> df)
def preprocess_prices(ticker_symbol, json_list):
    """
    * row data columns
    date,open_pric,high_pric,low_pric,close_pric,pred_rt,flu_rt,trde_qty,amt_mn,crd_rt,ind,
    orgn,for_qty,frgn,prm,for_rt,for_poss,for_wght,for_netprps,orgn_netprps,ind_netprps,crd_remn_rt

    
    * daliy_price columns(after preprocessing)
    id,stock_id,date,open_price,high_price,low_price,close_price,trde_qty,created_at,updated_at
    """
    df = pd.DataFrame(json_list)

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

    df['ticker_symbol'] = ticker_symbol
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    now = datetime.now()
    df['created_at'] = now
    df['updated_at'] = now

    final_columns = [
        "ticker_symbol","date","open_price","high_price","low_price","close_price",
        "trde_qty","created_at","updated_at"
    ]
    
    return df[final_columns]

# 최초 price data DB저장
def save_bulk_price_to_db(df):
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

# price data DB 저장
def save_price_to_db(df):
    session = SessionLocal()
    try:
        data_list = df.to_dict(orient = 'records')

        query = text("""
            INSERT IGNORE INTO daily_price
            (ticker_symbol, date, open_price, high_price, low_price, close_price, trde_qty, created_at, updated_at)
            VALUES(:ticker_symbol, :date, :open_price, :high_price, :low_price, :close_price, :trde_qty, :created_at, :updated_at)
        """)

        session.execute(query, data_list)
        session.commit()
        print(f"succeded saving {df['ticker_symbol'][0]} ")
    except Exception as e:
        session.rollback()
        print(f"Error during saving price data to DB : {e}")
    finally:
        session.close()

# 데이터 수집 메인 오케스트라
def fetch_daily_prices(ticker_symbol):
    # 데이터 수집 시작 날짜 구하기
    start_date = get_latest_date(ticker_symbol)

    if not start_date:
        start_date = datetime(2024,12,1).date()

    current_date = datetime.now().date()

    # 엑세스 토큰 조회
    ACCESS_TOKEN = fn_au10001()

    all_data = []
    while current_date >= start_date:

        # 주가 조회 파라미터
        qry_dt = current_date.strftime('%Y%m%d')
        cont_yn = 'N'
        next_key = ''
        
        params = {
            'stk_cd': ticker_symbol,
            'qry_dt': qry_dt,
            'indc_tp': '0',
        }

        res_json, cont_yn_res, next_key_res = fn_ka10086(ACCESS_TOKEN, params, cont_yn, next_key)

        if res_json is None:
            break
        print(res_json)
        daily = res_json.get('daly_stkpc',[])
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


    return ticker_symbol, all_data