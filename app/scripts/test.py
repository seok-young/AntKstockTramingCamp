from app.service.analysis import (
    get_target_stocksList,
    get_price,
    cal_MA,
    cal_MACD,
    cal_RSI_14,
    cal_Bollinger_band,
    save_analysis_to_DB,
)
from app.service.database import Base,engine


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    stock_list = get_target_stocksList()
    print(f"Target Stocks: {stock_list}")
    for stock in stock_list:
        try:
            print(f"Analysing {stock}")
            target = get_price(stock)
            target_MA=cal_MA(target)
            target_MA_MACD = cal_MACD(target_MA)
            target_MA_MACD_RSI = cal_RSI_14(target_MA_MACD)
            target_MA_MACD_RSI_Bol = cal_Bollinger_band(target_MA_MACD_RSI)
            print(f"Start Saving analysis ({stock})")
            save_analysis_to_DB(target_MA_MACD_RSI_Bol)
        except Exception as e:
            print(f"Error Saving Analysis to DB - {stock},{e}")
            continue

    # target = get_price("000270")
    # print(f"target = {target.tail().to_string()}, info = {target.info()}")

    # target_MA=cal_MA(target)
    # print(f"target_MA = {target_MA.tail().to_string()}, info = {target_MA.info()}")

    # target_MA_MACD = cal_MACD(target_MA)
    # print(f"target_MA_MACD = {target_MA_MACD.tail().to_string()}, info = {target_MA_MACD.info()}")

    # target_MA_MACD_RSI = cal_RSI_14(target_MA_MACD)
    # print(f"target_MA_MACD_RSI = {target_MA_MACD_RSI.tail().to_string()}, info = {target_MA_MACD_RSI.info()}")

    # target_MA_MACD_RSI_Bol = cal_Bollinger_band(target_MA_MACD_RSI)
    # print(f"target = {target_MA_MACD_RSI_Bol.tail().to_string()}, info = {target_MA_MACD_RSI_Bol.info()}")

    # save_analysis_to_DB(target_MA_MACD_RSI_Bol)

    