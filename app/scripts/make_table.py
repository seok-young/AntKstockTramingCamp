from app.core.database import (
    Base,
    engine,
    SessionLocal
)


# DB에 포트폴리오,계좌 테이블 생성
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

