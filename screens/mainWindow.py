import customtkinter as ctk
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

        # список последних трат
        """self.list_frame = ctk.CTkFrame(self)
        self.list_frame.pack(pady=10, padx=10, fill="both", expand=False)"""
        """self.misc_frame = ctk.CTkFrame(self, height=800, width=300)
        self.misc_frame.pack()"""

        self.list_frame = ctk.CTkFrame(self, height=800, width=300)
        self.list_frame.place(relx=0.78, rely=0)

        ctk.CTkLabel(self.list_frame, text="Последние операции:", anchor="w").pack(fill="x", padx=8, pady=(6,0))
        self.transactions_box = ctk.CTkTextbox(self.list_frame, width=400, height=600)
        self.transactions_box.pack(padx=8, pady=8)
        self.transactions_box.configure(state="disabled")

        # Кнопки
        btn_frame = ctk.CTkFrame(self)
        btn_frame.place(relx=0.4, rely=0.95)
        ctk.CTkButton(btn_frame, text="Добавить расход", command=self.add_expense).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Добавить доход", command=self.add_income).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Выйти", command=self.logout_callback).pack(side="left", padx=8)

        self.refresh_transactions()

    def refresh_transactions(self):
        self.transactions_box.configure(state="normal")
        self.transactions_box.delete("0.0", "end")

        db = SessionLocal()
        try:
            txs = db.query(Transaction).filter(Transaction.user_id == self.user.id).order_by(Transaction.timestamp.desc()).limit(10).all()
            for t in txs:
                ts = t.timestamp.strftime("%Y-%m-%d %H:%M")
                line = f"{ts} | {t.type} | {t.category or ''} | {t.amount}\n"
                self.transactions_box.insert("end", line)
        finally:
            db.close()

        self.transactions_box.configure(state="disabled")

    def add_expense(self):
        from tkinter.simpledialog import askstring
        amount = askstring("Добавить расход", "Сумма:")
        if amount:
            try:
                val = float(amount)
            except ValueError:
                return
            db = SessionLocal()
            try:
                new = Transaction(amount=val, category="Остальное", type="Расход", user_id=self.user.id)
                db.add(new); db.commit()
            finally:
                db.close()
            self.refresh_transactions()

    def add_income(self):
        from tkinter.simpledialog import askstring
        amount = askstring("Добавить доход", "Сумма:")
        if amount:
            try:
                val = float(amount)
            except ValueError:
                return
            db = SessionLocal()
            try:
                new = Transaction(amount=val, category="Остальное", type="Доход", user_id=self.user.id)
                db.add(new); db.commit()
            finally:
                db.close()
            self.refresh_transactions()
