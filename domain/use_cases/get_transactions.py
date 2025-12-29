from datetime import datetime, timedelta

class GetTransactionsUseCase:
    def __init__(self, transaction_repository):
        self.repo = transaction_repository

    def filter_by_period(self, user_id: int, tx_type: str, period: str):
        txs = self.repo.get_by_user_and_type(user_id, tx_type)

        if period == "Все время":
            return txs

        now = datetime.now()

        if period == "День":
            border = now - timedelta(days=1)
        elif period == "Неделя":
            border = now - timedelta(weeks=1)
        elif period == "Месяц":
            border = now - timedelta(days=30)
        elif period == "Год":
            border = now - timedelta(days=365)
        else:
            return txs # Все время

        return [t for t in txs if t.timestamp >= border]
