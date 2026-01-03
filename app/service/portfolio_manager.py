from app.core.database import SessionLocal,Base,engine

# DB에 테이블 생성
def make_portfolio_table():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:

        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error during making portfolio table : {e}")
        raise
    finally:
        session.close()
    
    return

# 매수 기록
def log_buying():

    
    return

# 매도 기록
def log_selling():
    return