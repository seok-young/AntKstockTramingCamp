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

from app.service.recommend import (
    get_recent_analysis,
    validate_buy_strategy,
    save_buy_rec
)


if __name__ == '__main__':
    # Base.metadata.create_all(bind=engine)
    # stock_list = get_target_stocksList()
    # print(f"Target Stocks: {stock_list}")
    # for stock in stock_list:
    #     try:
    #         print(f"Analysing {stock}")
    #         target = get_price(stock)
    #         target_MA=cal_MA(target)
    #         target_MA_MACD = cal_MACD(target_MA)
    #         target_MA_MACD_RSI = cal_RSI_14(target_MA_MACD)
    #         target_MA_MACD_RSI_Bol = cal_Bollinger_band(target_MA_MACD_RSI)
    #         print(f"Start Saving analysis ({stock})")
    #         save_analysis_to_DB(target_MA_MACD_RSI_Bol)
    #     except Exception as e:
    #         print(f"Error Saving Analysis to DB - {stock},{e}")
    #         continue
    stock_list = [
        '000270','000660','001500','005490','005930','006400',
        '009150','009540','009830','010950','011170','011200',
        '012330','018880','032830','033780','034220','034730',
        '035420','035720','035760','051900','051910','055550',
        '066570','069500','086280','086520','086790','090430',
        '091160','091170','096770','097950','102110','105560',
        '112040','132030','143860','196170','207940','228800',
        '229200','247540','263750','323410','357780','360750',
        '377300','469790'
    ]
    for stock in stock_list:
        analysis = get_recent_analysis(stock)
        # print(analysis)
        analysis, answer=validate_buy_strategy(analysis)
        print(answer)
        if answer:
            print(f"starting save recommendation -> analysis id : {analysis['id']}")
            save_buy_rec(analysis)
