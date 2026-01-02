import datetime as dt
import pandas as pd
import numpy as np
from sqlalchemy import desc

from app.core.database import SessionLocal,Base,engine
from app.model import Analysis,Recommendation

# analysis 테이블에서 최신 데이터 조회
def get_recent_analysis(stock_id):
    session=SessionLocal()
    try:
        result = session.query(Analysis).filter(Analysis.stock_id == stock_id) \
                        .order_by(desc(Analysis.date)).first()
        if result:
            result_dict = {col.name: getattr(result, col.name) for col in result.__table__.columns}
        return result_dict
    except Exception as e:
        print(f"Error during getting recent analysis stockcode = {stock_id} : {e}")
        return {}
    finally:
        session.close()

# 매수 조건 따지기
"""
    * 매수 조건 : 필수 3가지 모두 충족 & 보조 중 1가지 충족 

    <필수>
    1. 주가 > 120일 이평선 (1년치 데이터 활용: 장기 상승장인 종목만 선정)
    2. 20일 이평선 > 60일 이평선 (중기 정배열: 상승 에너지가 유지됨)
    3. MACD 선 > 시그널 선 (상승 모멘텀 확인)

    <보조>
    1. RSI: 50 이하 (과열되지 않은 적정 가격)
    2. 볼린저: 주가가 중심선(20일선) 이하 또는 현재가 <= 하단 밴드 * 1.02
"""
def validate_buy_strategy(analysis_dict):
    buy_signal = False

    requires = [
        analysis_dict['close_price'] > analysis_dict['ma120'],
        analysis_dict['ma20'] > analysis_dict['ma60'],
        analysis_dict['macd'] > analysis_dict['macd_signal']
    ]

    assists = [
        analysis_dict['rsi'] <= 60,
        (analysis_dict['close_price'] <= analysis_dict['bb_middle']) or 
        (analysis_dict['close_price'] <= (analysis_dict['bb_lower'] * 1.02))
    ]

    if all(requires) and any(assists):
        buy_signal = True

    return analysis_dict, buy_signal

# recommend DB 저장
def save_buy_rec(analysis_dict):
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try: 
        new_rec = Recommendation(
            stock_id = analysis_dict['stock_id'],
            analysis_id = analysis_dict['id'],
            signal_type = "BUY",
            price = analysis_dict['close_price'],
            base_date = analysis_dict['date'],
    )
        session.add(new_rec)
        session.commit()
        print(f"saved buy rec successfully -> analysis_id : {analysis_dict['id']}")
    except Exception as e:
        session.rollback()
        if "UniqueConstraint" not in str(e):
            print(f" 저장 에러 ({analysis_dict['stock_id']}): {e}")
    finally:
        session.close()



# 매도 조건 따지기
"""
    * 매도 조건 : 필수 중 1가지 충족
    * 익절 조건 : 보조 중 1가지 충족

    <필수>
    1. 주가 < 20일 이평선 하향 돌파 (한 달 추세 무너짐)
    2. MACD 선 < 시그널 선 (데드크로스 발생)
    3. 현재가 < 매수가 * 0.93 (기계적 -7% 손절선, 강제손절선)

    <보조>
    1. 볼린저 밴드: 주가가 상단 밴드 터치 후 재진입
    2. RSI: 75 이상 (단기 과열로 인한 매도 알림)
"""
def validate_sell_strategy():
    sell_signal = False
    return sell_signal