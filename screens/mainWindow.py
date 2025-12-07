import customtkinter as ctk
from unicodedata import category

from database.db import SessionLocal
from database.models import Transaction
from datetime import datetime

class MainFrame(ctk.CTkFrame):
    def __init__(self, master, user, logout_callback):
        super().__init__(master)
        self.user = user
        self.logout_callback = logout_callback

        self.pack(fill="both", expand=True)

        ctk.CTkLabel(self, text=f"Добро пожаловать, {user.email}", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        self.mode_var = ctk.StringVar(value="Траты")

        self.segment = ctk.CTkSegmentedButton(
            self,
            values=["Траты", "Доходы"],
            variable=self.mode_var,
            command=self.on_mode_change
        )
        self.segment.place(relx=0.5, rely=0.05, anchor="center")

        # список последних трат
        self.list_frame = ctk.CTkFrame(self, height=800, width=300)
        self.list_frame.place(relx=0.78, rely=0)

        ctk.CTkLabel(self.list_frame, text="Последние операции:", anchor="w").pack(fill="x", padx=8, pady=(6,0))
        self.transactions_box = ctk.CTkTextbox(self.list_frame, width=400, height=600)
        self.transactions_box.pack(padx=8, pady=8)
        self.transactions_box.configure(state="disabled")

        # Кнопки
        btn_frame = ctk.CTkFrame(self)
        btn_frame.place(relx=0.4, rely=0.95)
        self.add_btn = ctk.CTkButton(btn_frame, text="Добавить расход", command=self.add_expense)
        self.add_btn.pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Выйти", command=self.logout_callback).pack(side="left", padx=8)

        self.refresh_transactions()

    def on_mode_change(self, mode):
        self.refresh_transactions()  # фильтруем список

        if mode == "Траты":
            self.add_btn.configure(text="Добавить расход", command=self.add_expense)
        else:
            self.add_btn.configure(text="Добавить доход", command=self.add_income)

    def refresh_transactions(self):
        self.transactions_box.configure(state="normal")
        self.transactions_box.delete("0.0", "end")

        mode = self.mode_var.get()
        tx_type = "expense" if mode == "Траты" else "income"

        db = SessionLocal()
        try:
            txs = (
                db.query(Transaction)
                .filter(
                    Transaction.user_id == self.user.id,
                    Transaction.type == tx_type
                )
                .order_by(Transaction.timestamp.desc())
                .limit(10)
                .all()
            )

            for t in txs:
                ts = t.timestamp.strftime("%Y-%m-%d %H:%M")
                line = f"{ts} | {t.category or ''} | {t.amount}\n"
                self.transactions_box.insert("end", line)

        finally:
            db.close()

        self.transactions_box.configure(state="disabled")

    def add_expense(self):
        self.open_add_dialog("expense")

    def add_income(self):
        self.open_add_dialog("income")

    def open_add_dialog(self,tx_type):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Новая операция")
        dialog.geometry("400x250")
        dialog.grab_set()

        label_text = "Введите сумму расхода:" if tx_type == "expense" else "Введите сумму дохода:"
        ctk.CTkLabel(dialog, text=label_text).pack(pady=5)

        amount_entry = ctk.CTkEntry(dialog)
        amount_entry.pack(pady=5)

        if tx_type == "expense":
            categories = [ "Транспорт","Продукты", "Развлечения", "Кафе", "Здоровье", "Подписки", "Одежда", "Другое"]
        else:
            categories = ["Зарплата", "Перевод", "Подарок", "Премия"]

        category_var = ctk.StringVar(value=categories[1])

        ctk.CTkLabel(dialog, text="Категория:").pack(pady=5)

        category_menu = ctk.CTkOptionMenu(dialog, variable=category_var, values=categories)
        category_menu.pack(pady=5)

        def submit():
            try:
                amount = float(amount_entry.get())
            except ValueError:
                return
            category = category_var.get()

            db = SessionLocal()
            try:
                new = Transaction(
                    amount=amount,
                    category=category,
                    type=tx_type,
                    user_id=self.user.id
                )
                db.add(new)
                db.commit()
            finally:
                db.close()

            dialog.destroy()
            self.refresh_transactions()

        ctk.CTkButton(dialog, text="Добавить", command=submit).pack(pady=5)
