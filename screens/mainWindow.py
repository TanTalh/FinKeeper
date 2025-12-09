import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image
from datetime import datetime, timedelta
from database.db import SessionLocal
from database.models import Transaction


CATEGORY_COLORS = {
    "Продукты": "#FF6B6B",
    "Транспорт": "#4ECDC4",
    "Развлечения": "#FFD93D",
    "Кафе/рестораны": "#FF9F1C",
    "Здоровье": "#5F6FFF",
    "Подписки": "#9D4EDD",
    "Одежда": "#FF577F",
    "Другое": "#A0A0A0",
    "Зарплата": "#2ECC71",
    "Перевод": "#3498DB",
}


class MainFrame(ctk.CTkFrame):
    def __init__(self, master, user, logout_callback):
        super().__init__(master)
        self.user = user
        self.logout_callback = logout_callback

        self.chart_canvas = None
        self.animation = None
        self.pack(fill="both", expand=True)


        # Фрейм с парсером(в будущем) и настройками
        self.left_menu = ctk.CTkFrame(self, width=200, fg_color="#1a1a1a")
        self.left_menu.pack(side="left", fill="y")

        # Фрейм добавления операции
        self.add_operation_frame = ctk.CTkFrame(self, height=100, width=372, fg_color="#023E8A", corner_radius=40 )
        self.add_operation_frame.place(relx=0.4, rely=0.85)

        # Фрейм с балансом
        self.balance_frame = ctk.CTkFrame(self, width=200,height=70, corner_radius=30)
        self.balance_frame.place(relx=0.65, rely=0.05)

        # Изображения
        self.vector_img = ctk.CTkImage(dark_image=Image.open("images/vector.png"), size=(40, 35))
        self.expense_img = ctk.CTkImage(dark_image=Image.open("images/expense.png"), size=(50,50))
        self.income_img = ctk.CTkImage(dark_image=Image.open("images/income.png"), size=(50,50))

        # Переключатель режимов
        self.mode_var = ctk.StringVar(value="Траты")
        self.segment = ctk.CTkSegmentedButton(
            self,
            height=70,
            width=300,
            corner_radius=50,
            values=["Траты", "Доходы"],
            variable=self.mode_var,
            font=ctk.CTkFont(family="inter", size=25),
            command=self.on_mode_change
        )
        self.segment.place(relx=0.5, rely=0.08, anchor="center")

        # Выпадающий список с операциями за разный период
        self.period_var = ctk.StringVar(value="Все время")
        self.period_menu = ctk.CTkOptionMenu(self,
                                             variable=self.period_var,
                                             values=["День","Неделя","Месяц","Год","Все время"],
                                             command= lambda _: self.refresh_all())
        self.period_menu.place(relx=0.25, rely=0.2)

        # Расположение диаграммы
        self.chart_frame = ctk.CTkFrame(self, width=650, height=450, fg_color="transparent")
        self.chart_frame.place(relx=0.5, rely=0.56, anchor="center")


        # Список транзакций
        self.right_frame = ctk.CTkFrame(self, width=400, fg_color="transparent")
        self.right_frame.pack(side="right", fill="y")

        ctk.CTkLabel(self.right_frame, text="Последние операции:",
                     font=ctk.CTkFont(size=16)).pack(anchor="w", padx=10, pady=10)

        self.transactions_area = ctk.CTkScrollableFrame(
            self.right_frame,
            width=400,
            fg_color="transparent"
        )
        self.transactions_area.pack(fill="both", expand=True, padx=10)

        # виджет баланса
        self.balance_label = ctk.CTkLabel(self.balance_frame,
                                          text="Баланс: 0 ₽",
                                          font=ctk.CTkFont(family="inter", weight="bold", size=16),
                                          text_color="white")
        self.balance_label.place(relx=0.1, rely=0.3)
        # Нижние кнопки
        self.add_btn = ctk.CTkButton(self.add_operation_frame,
                                     height=50,
                                     width=170,
                                     fg_color="#0077B6",
                                     corner_radius=20,
                                     font=ctk.CTkFont(family="inter", size=18),
                                     text="Добавить трату",
                                     command=self.add_expense)
        self.add_btn.place(relx=0.27, rely=0.5, anchor="center")

        self.exit_btn = ctk.CTkButton(self.left_menu,
                                      width=290,
                                      height=40,
                                      text="Выйти",
                                      font=ctk.CTkFont(family="inter",weight="bold", size=30),
                                      command=self.logout_callback)
        self.exit_btn.place(relx=0.5, rely=1, anchor="s")

        ctk.CTkLabel(self.add_operation_frame, image=self.vector_img, text="").place(relx=0.55, rely=0.3)
        self.operation = ctk.CTkLabel(self.add_operation_frame, image=self.expense_img, text="")
        self.operation.place(relx=0.75, rely=0.25,)




        # Первичная загрузка
        self.refresh_all()

    def refresh_all(self):
        self.refresh_transactions()
        self.update_balance()
        self.update_pie_chart()



    def on_mode_change(self, mode):
        if mode == "Траты":
            self.add_btn.configure(text="Добавить трату",font=ctk.CTkFont(family="inter", size=18), command=self.add_expense)
            self.operation.configure(image=self.expense_img)
        else:
            self.add_btn.configure(text="Добавить доход",font=ctk.CTkFont(family="inter", size=18), command=self.add_income)
            self.operation.configure(image=self.income_img)

        self.refresh_all()

    # создание карточки операции
    def create_tx_card(self, parent, tx):
        color = CATEGORY_COLORS.get(tx.category, "#888888")
        ts = tx.timestamp.strftime("%Y-%m-%d %H:%M")

        frame = ctk.CTkFrame(parent, fg_color=color, corner_radius=14)
        frame.pack(fill="x", pady=6)

        ctk.CTkLabel(frame, text=tx.category, text_color="white",
                     font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(6, 0))
        ctk.CTkLabel(frame, text=f"{tx.amount} ₽", text_color="white",
                     font=("Arial", 13)).pack(anchor="w", padx=10)
        ctk.CTkLabel(frame, text=ts, text_color="white",
                     font=("Arial", 10)).pack(anchor="w", padx=10, pady=(0, 6))

    def filter_by_period(self, txs):
        now = datetime.now()
        period = self.period_var.get()

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

    #  функция обновления
    def refresh_transactions(self):
        for w in self.transactions_area.winfo_children():
            w.destroy()

        mode = self.mode_var.get()
        tx_type = "expense" if mode == "Траты" else "income"

        db = SessionLocal()
        try:
            txs = (
                db.query(Transaction)
                .filter(Transaction.user_id == self.user.id, Transaction.type == tx_type)
                .order_by(Transaction.timestamp.desc())
                .all()
            )
        finally:
            db.close()

        txs = self.filter_by_period(txs)

        for t in txs:
            self.create_tx_card(self.transactions_area, t)


    #  круговая диаграмма
    def update_pie_chart(self):
        mode = self.mode_var.get()
        tx_type = "expense" if mode == "Траты" else "income"

        db = SessionLocal()
        try:
            txs = db.query(Transaction).filter(
                Transaction.user_id == self.user.id,
                Transaction.type == tx_type
            ).all()
        finally:
            db.close()

        txs = self.filter_by_period(txs)

        # группировка по категориям
        categories = {}
        for t in txs:
            categories[t.category] = categories.get(t.category, 0) + t.amount

        # удаление старого холста
        if self.chart_canvas:
            try:
                self.chart_canvas.get_tk_widget().destroy()
            except Exception:
                pass
            self.chart_canvas = None

        if not categories:
            return

        labels = list(categories.keys())
        values = list(categories.values())
        colors = [CATEGORY_COLORS.get(c, "#888888") for c in labels]


        fig = Figure(figsize=(5.5, 5.5), dpi=100)

        ax = fig.add_axes([0.0, 0.0, 0.78, 1.0])  # оставил место для легенды

        # прозрачные фоны
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

        # создание пирога
        wedges, texts, autotexts = ax.pie(
            values,
            labels=None,
            colors=colors,
            startangle=90,
            autopct='%1.1f%%',
            pctdistance=0.75,
            labeldistance=1.05,
            textprops={'color': 'white', 'fontsize': 11}
        )

        ax.set_aspect('equal')  # гарантирует круг

        ax.legend(
            wedges,
            labels,
            title='Категории',
            loc='upper left',
            bbox_to_anchor=(1.02, 0.9),
            frameon=False,
            fontsize=10,
            labelcolor='black',
            handlelength=1.5,
            handleheight=1.2,
            handletextpad=0.5,
            labelspacing=0.7
        )

        # создание canvas
        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.chart_canvas.draw()

        canvas_widget = self.chart_canvas.get_tk_widget()
        # размещение canvas по центру chart_frame и задаю его размер как у frame
        canvas_widget.place(relx=0.5, rely=0.5, anchor="center")
        canvas_widget.configure(width=650, height=450)

    def add_expense(self):
        self.open_add_dialog("расход", list(CATEGORY_COLORS.keys()))

    def add_income(self):
        self.open_add_dialog("доход", ["Зарплата", "Перевод"])

    # Универсальное окно добавления
    def open_add_dialog(self, tx_type, categories):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Новый {tx_type}")
        dialog.geometry("400x250")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Введите сумму:").pack(pady=5)
        amount_entry = ctk.CTkEntry(dialog)
        amount_entry.pack(pady=5)

        ctk.CTkLabel(dialog, text="Категория:").pack(pady=5)
        category_var = ctk.StringVar(value=categories[0])
        ctk.CTkOptionMenu(dialog, values=categories, variable=category_var).pack(pady=5)

        def submit():
            try:
                amount = float(amount_entry.get())
            except ValueError:
                return

            db = SessionLocal()
            try:
                tx = Transaction(
                    amount=amount,
                    category=category_var.get(),
                    type="income" if tx_type == "доход" else "expense",
                    user_id=self.user.id
                )
                db.add(tx)
                db.commit()
            finally:
                db.close()

            dialog.destroy()
            self.refresh_all()

        ctk.CTkButton(dialog, text="Добавить", command=submit).pack(pady=15)

    # Обновление баланса
    def update_balance(self):
        db = SessionLocal()
        try:
            income = db.query(Transaction).filter(
                Transaction.user_id == self.user.id,
                Transaction.type == "income"
            ).all()

            expense = db.query(Transaction).filter(
                Transaction.user_id == self.user.id,
                Transaction.type == "expense"
            ).all()
        finally:
            db.close()

        total_income = sum(t.amount for t in income)
        total_expense = sum(t.amount for t in expense)

        balance = total_income - total_expense

        color = "white"
        if balance > 0:
            color = "#54d98c"
        elif balance < 0:
            color = "#ec6670"
        self.balance_label.configure(
            text=f"Баланс: {balance:.2f} ₽",
            text_color=color
        )