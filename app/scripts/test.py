from datetime import datetime,date
from app.service.analysis import (
    get_target_stocksList,
    get_price,
    cal_MA,
    cal_MACD,
    cal_RSI_14,
    cal_Bollinger_band,
    save_analysis_to_db,
)
from app.core.database import Base,engine

from app.service.recommend import (
    get_recent_analysis,
    validate_buy_strategy,
    save_buy_rec
)

from app.service.notify import send_recommendation_alerts

from app.service.collector import (
    get_latest_date,
    get_interest_stocksID,
    fetch_daily_prices,
    preprocess_prices,
    save_price_to_db
    )

from app.core.config import settings
from app.main import daily_stock_routine
from app.service.portfolio_manager import make_portfolio_table



if __name__ == '__main__':
    
    # params_token = {
	# 	'grant_type': 'client_credentials',  
	# 	'appkey': settings.APP_KEY,
	# 	'secretkey': settings.SECRET_KEY
	# }
    # ACCESS_TOKEN = fn_au10001(params_token)

    # qry_dt = date(2025,12,30)
    # cont_yn = 'N'  # 해당 날짜 조회의 시작은 항상 'N'
    # next_key = ''      
        
    # params = {
    #     'stk_cd': '005930',
    #     'qry_dt': qry_dt.strftime("%Y%m%d"),
    #     'indc_tp': '0',
    # }
        

    # result=fn_ka10086(ACCESS_TOKEN,params,cont_yn,next_key) 
    # print(result)

    # daily_stock_routine()
    make_portfolio_table()