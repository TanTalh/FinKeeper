class GroupByCategoryUseCase:
    def group_by_category(self, transactions):
        categories = {}

        for t in transactions:
            categories[t.category] = categories.get(t.category, 0) + t.amount

        labels = list(categories.keys())
        values =list(categories.values())

        return labels, values