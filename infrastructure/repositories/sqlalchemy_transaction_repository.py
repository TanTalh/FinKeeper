from data.database.db import SessionLocal
from data.models.models import Transaction

class SqlAchemyTransactionRepository:
    def get_by_user_and_type(self, user_id: int, tx_type: str):
        db = SessionLocal()
        try:
            return (
                db.query(Transaction)
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.type == tx_type
                )
                .order_by(Transaction.timestamp.desc())
                .all
            )
        finally:
            db.close()

    def add(self,user_id,amount,category,tx_type):
        db = SessionLocal()
        try:
            tx = Transaction(
                user_id=user_id,
                amount=amount,
                category=category,
                type=tx_type
            )
            db.add(tx)
            db.commit()
        finally:
            db.close()
