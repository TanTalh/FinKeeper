class AddTransactionUseCase:
    def __init__(self, transaction_repository):
        self.repo = transaction_repository

    def add_transaction(self, user_id,amount,category,tx_type):
        self.repo.add(
            user_id=user_id,
            amount=amount,
            category=category,
            tx_type=tx_type)
