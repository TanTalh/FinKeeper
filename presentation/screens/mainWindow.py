from doctest import master

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image
from datetime import datetime, timedelta
from domain.use_cases.get_transactions import GetTransactionsUseCase
from infrastructure.repositories.sqlalchemy_transaction_repository import SqlAchemyTransactionRepository
from domain.use_cases.calculate_balance import CalculateBalanceUseCase
from domain.use_cases.group_by_category import GroupByCategoryUseCase
from domain.use_cases.add_transaction import AddTransactionUseCase
from infrastructure.charts.pie_chart import build_pie_chart
from domain.constants import CATEGORY_COLORS


class MainFrame(ctk.CTkFrame):
    def __init__(self, master, user, logout_callback):
        super().__init__(master)
        self.user = user
        self.logout_callback = logout_callback

        self.chart_canvas = None
        self.animation = None
        self.pack(fill="both", expand=True)


        self.tx_repo = SqlAchemyTransactionRepository()
        self.add_tx_uc = AddTransactionUseCase(self.tx_repo)
        self.get_txs_uc = GetTransactionsUseCase(self.tx_repo)
        self.calc_balance_uc = CalculateBalanceUseCase(self.tx_repo)
        self.group_by_category_uc = GroupByCategoryUseCase()

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


    #  функция обновления
    def refresh_transactions(self):
        for w in self.transactions_area.winfo_children():
            w.destroy()

        mode = self.mode_var.get()
        tx_type = "expense" if mode == "Траты" else "income"
        period = self.period_var.get()

        txs = self.get_txs_uc.filter_by_period(
            user_id=self.user.id,
            tx_type=tx_type,
            period=period
        )

        for t in txs:
            self.create_tx_card(self.transactions_area, t)


    #  круговая диаграмма
    def update_pie_chart(self):
        mode = self.mode_var.get()
        tx_type = "expense" if mode == "Траты" else "income"
        period = self.period_var.get()

        txs = self.get_txs_uc.filter_by_period(user_id=self.user.id,
                                               tx_type=tx_type,
                                               period=period
                                               )


        # удаление старого холста
        if self.chart_canvas:
            try:
                self.chart_canvas.get_tk_widget().destroy()
            except Exception:
                pass
            self.chart_canvas = None

        if not txs:
            return

        labels, values = self.group_by_category_uc.group_by_category(txs)

        colors = [CATEGORY_COLORS.get(c, "#888888") for c in labels]


        fig = build_pie_chart(labels,values,colors)
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
            self.add_tx_uc.add_transaction(
                user_id=self.user.id,
                amount=amount,
                category=category_var.get(),
                tx_type="income" if tx_type == "доход" else "expense"
            )

            dialog.destroy()
            self.refresh_all()

        ctk.CTkButton(dialog, text="Добавить", command=submit).pack(pady=15)

    # Обновление баланса
    def update_balance(self):
        balance = self.calc_balance_uc.calculate_balance(self.user.id)

        color = "white"
        if balance > 0:
            color = "#54d98c"
        elif balance < 0:
            color = "#ec6670"

        self.balance_label.configure(
            text=f"Баланс: {balance:.2f} ₽",
            text_color=color
        )