class CalculateBalanceUseCase:
    def __init__(self, transaction_repository):
        self.repo = transaction_repository

    def calculate_balance(self, user_id: int) -> float:
        income = self.repo.get_by_user_and_type(user_id, "income")
        expense = self.repo.get_by_user_and_type(user_id, "expense")

        total_income = sum(t.amount for t in income)
        total_expense =sum(t.amount for t in expense)

        return total_income - total_expense