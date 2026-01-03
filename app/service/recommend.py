import datetime as dt
import pandas as pd
import numpy as np
from sqlalchemy import desc,text

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
def validate_buy_strategy(analysis_df):
    buy_signal = False

    requires = [
        analysis_df['close_price'] > analysis_df['ma120'],
        analysis_df['ma20'] > analysis_df['ma60'],
        analysis_df['macd'] > analysis_df['macd_signal']
    ]

    assists = [
        analysis_df['rsi'] <= 60,
        (analysis_df['close_price'] <= analysis_df['bb_middle']) or 
        (analysis_df['close_price'] <= (analysis_df['bb_lower'] * 1.02))
    ]

    if all(requires) and any(assists):
        buy_signal = True

    return analysis_df, buy_signal

# 처음 recommend DB 저장
def save_bulk_buy_rec(analysis_dict):
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try: 
        new_rec = Recommendation(
            ticker_symbol = analysis_dict['ticker_symbol'],
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
            print(f" 저장 에러 ({analysis_dict['ticker_symbol']}): {e}")
    finally:
        session.close()


def save_buy_rec(analysis_dict):
    session = SessionLocal()
    try: 
        # 이미 앞선 단계에서 analysis 저장 및 flush()가 완료되어 
        # analysis_dict['id']에 값이 들어있다고 가정합니다.
        
        query = text("""
            INSERT IGNORE INTO recommendation 
            (ticker_symbol, analysis_id, signal_type, strategy_name, price, base_date, is_sent, create_at)
            VALUES (:ticker_symbol, :analysis_id, :signal_type, :strategy_name, :price, :base_date, 0, NOW())
        """)
        
        session.execute(query, {
            'ticker_symbol': analysis_dict['ticker_symbol'],
            'analysis_id': analysis_dict['id'], 
            'signal_type': "BUY",
            'strategy_name':"BASIC",
            'price': analysis_dict['close_price'],
            'base_date': analysis_dict['date']
        })
        
        session.commit()
        # 성공 로그만 간단히 남깁니다.
        print(f"succeded save recommendation ({analysis_dict['ticker_symbol']})")

    except Exception as e:
        session.rollback()
        print(f"Error during saving recommendation ({analysis_dict.get('ticker_symbol')}): {e}")
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