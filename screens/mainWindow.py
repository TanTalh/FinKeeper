import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from PIL import Image
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
        self.pack(fill="both", expand=True)


        # Фрейм с парсером(в будущем) и настройками
        self.left_menu = ctk.CTkFrame(self, width=200, fg_color="#1a1a1a")
        self.left_menu.pack(side="left", fill="y")

        self.add_operation_frame = ctk.CTkFrame(self, height=100, width=372, fg_color="#023E8A", corner_radius=40 )
        self.add_operation_frame.place(relx=0.4, rely=0.85)

        # Изображения
        self.vector_img = ctk.CTkImage(dark_image=Image.open("images/vector.png"), size=(40, 35))
        self.expense_img = ctk.CTkImage(dark_image=Image.open("images/expense.png"), size=(50,50))
        self.income_img = ctk.CTkImage(dark_image=Image.open("images/income.png"), size=(55,60))

        # Переключатель режимов
        self.mode_var = ctk.StringVar(value="Траты")
        self.segment = ctk.CTkSegmentedButton(
            self,
            height=70,
            width=300,
            corner_radius=50,
            values=["Траты", "Доходы"],
            variable=self.mode_var,
            command=self.on_mode_change
        )
        self.segment.place(relx=0.5, rely=0.08, anchor="center")

        # Расположение диаграммы
        self.chart_frame = ctk.CTkFrame(self,)
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


        # Нижние кнопки
        self.add_btn = ctk.CTkButton(self.add_operation_frame,
                                     height=50,
                                     width=150,
                                     fg_color="#0077B6",
                                     corner_radius=20,
                                     text="Добавить трату",
                                     command=self.add_expense)
        self.add_btn.place(relx=0.25, rely=0.5, anchor="center")

        self.exit_btn = ctk.CTkButton(self.left_menu,width=290, height=40, text="Выйти", command=self.logout_callback)
        self.exit_btn.place(relx=0.5, rely=1, anchor="s")

        ctk.CTkLabel(self.add_operation_frame, image=self.vector_img, text="").place(relx=0.55, rely=0.3)
        self.operation = ctk.CTkLabel(self.add_operation_frame, image=self.expense_img, text="")
        self.operation.place(relx=0.75, rely=0.25, anchor="n")


        # Первичная загрузка
        self.refresh_transactions()
        self.update_pie_chart()



    def on_mode_change(self, mode):
        if mode == "Траты":
            self.add_btn.configure(text="Добавить трату", command=self.add_expense)
            self.operation.configure(image=self.expense_img)
        else:
            self.add_btn.configure(text="Добавить доход", command=self.add_income)
            self.operation.configure(image=self.income_img)

        self.refresh_transactions()
        self.update_pie_chart()

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

        categories = {}
        for t in txs:
            categories[t.category] = categories.get(t.category, 0) + t.amount

        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()

        if not categories:
            return

        labels = list(categories.keys())
        values = list(categories.values())
        colors = [CATEGORY_COLORS.get(c, "#888888") for c in labels]

        fig = Figure(figsize=(4, 4), dpi=100)
        ax = fig.add_subplot(111)
        fig.patch.set_facecolor("none")
        ax.set_facecolor("none")

        wedges, texts, autotexts = ax.pie(
            values,
            colors=colors,
            startangle=90,
            autopct='%1.1f%%',
            textprops={'color': 'white', 'fontsize': 12}
        )

        def animate(i):
            alpha = i / 20
            for w in wedges:
                w.set_alpha(alpha)
            for t in autotexts:
                t.set_alpha(alpha)
            return wedges + autotexts

        FuncAnimation(fig, animate, frames=20, interval=20, blit=False)

        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack()


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
            self.refresh_transactions()
            self.update_pie_chart()

        ctk.CTkButton(dialog, text="Добавить", command=submit).pack(pady=15)
