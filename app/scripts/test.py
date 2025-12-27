from app.service.analysis import (
    get_price,
    cal_MA,
    cal_MACD,
    cal_RSI_14,
    cal_Bollinger_band,
)


if __name__ == '__main__':
    target = get_price("000270")
    print(f"target = {target.tail().to_string()}, info = {target.info()}")

    target_MA=cal_MA(target)
    print(f"target_MA = {target_MA.tail().to_string()}, info = {target_MA.info()}")

    target_MA_MACD = cal_MACD(target_MA)
    print(f"target_MA_MACD = {target_MA_MACD.tail().to_string()}, info = {target_MA_MACD.info()}")

    target_MA_MACD_RSI = cal_RSI_14(target_MA_MACD)
    print(f"target_MA_MACD_RSI = {target_MA_MACD_RSI.tail().to_string()}, info = {target_MA_MACD_RSI.info()}")

    target_MA_MACD_RSI_Bol = cal_Bollinger_band(target_MA_MACD_RSI)
    print(f"target = {target_MA_MACD_RSI_Bol.tail().to_string()}, info = {target_MA_MACD_RSI_Bol.info()}")


    