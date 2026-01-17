from sqlalchemy import desc
from datetime import datetime

from app.model import Portfolio,AccountHistory


class TradeManager:
    def __init__(self, session):
        self.session = session


    def _get_latest_balance(self):
        last_history = self.session.query(AccountHistory)\
            .order_by(desc(AccountHistory.transaction_date), desc(AccountHistory.id))\
            .first()

        if last_history:
            return last_history.balance
        else:
            return 0.0

    """

        현금 입출금 기록

    """

    def record_cash_flow(self, data: dict):
        try:
            cur_balance = self._get_latest_balance()
        
            if data['transaction_type'] == 'WITHDRAWAL':
                amount_change = -1 * (data['amount'])
            else:
                amount_change = (data['amount'])

            new_balance = cur_balance + amount_change
            now = datetime.now()

            history = AccountHistory(
                transaction_type=data['transaction_type'],
                amount=amount_change,
                balance=new_balance,
                transaction_date=now

            )

            self.session.add(history)
            self.session.commit()

            print(f"[{data['transaction_type']}] - [{data['amount']}원] 처리완료")
        except Exception as e:
            self.session.rollback()
            print(f"Error during recording cash flow : {e}")



    """

        주식 매매 기록

    """

    def execute_trade(self, trade_data: dict):
        """
        trade_data 예시:
        {
            ticker_symbol: '005930',
            rec_id: 2,
            qty: 10,
            price: 110000
            transaction_type: 'BUY'
        }
        """
        try:
            # 현재 잔액 조회
            cur_balance = self._get_latest_balance()

            # 거래 금액 계산
            total_amount = trade_data.qty * trade_data.price
            
            if trade_data.transaction_type == 'BUY':
                amount_change = -total_amount
            else:
                amount_change = total_amount

            # 새로운 잔액 계산
            new_balance = cur_balance + amount_change

            # 거래 기록
            if trade_data.transaction_type == 'BUY':
                self._handle_buy(trade_data,new_balance, amount_change)
            elif trade_data.transaction_type == 'SELL':
                self._handle_sell(trade_data,new_balance, amount_change)

            self.session.commit()
            print(f"[{trade_data.ticker_symbol}] - [{trade_data.transaction_type}] 처리 완료")
        except Exception as e:
            self.session.rollback()
            print(f"Error during executing trade : {e}" )
            raise
        
        
    def _handle_buy(self, data, new_balance, amount_change):
        now = datetime.now()

        # Portfolio
        new_port = Portfolio(
            ticker_symbol = data.ticker_symbol,
            recommendation_id = data.rec_id,
            quantity = data.qty,
            buy_price = data.price,
            buy_date = now,
            is_active = 1
        )
        self.session.add(new_port)
        self.session.flush()

        # Account History
        history = AccountHistory(
            portfolio_id = new_port.id,
            transaction_type='BUY',
            amount = amount_change,
            balance = new_balance,
            transaction_date = now
        )
        self.session.add(history)
    
    def _handle_sell(self, data, new_balance, amount_change):
        now = datetime.now()

        # Portfolio
        port = self.session.query(Portfolio).filter_by(
            recommendation_id=data['rec_id'], is_active=1
        ).first()

        if not port:
            raise Exception("매도할 포트폴리오를 찾을 수 없습니다.")

        port.sell_price = data['price']
        port.sell_date = now
        port.is_active = 0

        # Account History
        history = AccountHistory(
            portfolio_id = port.id,
            transaction_type='SELL',
            amount = amount_change,
            balance = new_balance,
            transaction_date = now
        )
        self.session.add(history)

    """

        가상정산

    """

    def calculate_virtual_balance(self, virtual_balance, trade_data: dict):
        """
        trade_data 예시:
        {
            ticker_symbol: '005930',
            rec_id: 2,
            qty: 10,
            price: 110000
            transaction_type: 'BUY'
        }
        """
        try:
            # 거래 금액 계산
            total_amount = trade_data.qty * trade_data.price
            
            if trade_data.transaction_type == 'BUY':
                amount_change = -total_amount
            else:
                amount_change = total_amount

            # 새로운 잔액 계산
            new_balance = virtual_balance + amount_change

        except Exception as e:            
            print(f"Error during calculating virtual balance : {e}" )
            raise

        return new_balance
