import customtkinter as ctk
from PIL import Image
from database.db import SessionLocal
from database.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, switch_to_main_callback):
        super().__init__(master)
        self.switch_to_main = switch_to_main_callback


        self.pack(fill="both", expand=True)

        auth_frame = ctk.CTkFrame(self, height=500, width=610, fg_color="#2c2c2c", corner_radius=55)
        auth_frame.pack_propagate(False)
        auth_frame.place(rely=0.5, relx=0.5, anchor="center")


        ctk.CTkLabel(auth_frame, text="Авторизация", width=100, height=80, font=("inter", 32),
                                 text_color="white", ).place(rely=0.05, relx=0.1)

        self.email_entry = ctk.CTkEntry(auth_frame, height=40, width=450,
                                           placeholder_text="example@gmail.com",
                                           placeholder_text_color="#D9D9D9",
                                           font=("inter", 25),
                                           fg_color="#3B3B3B",
                                           text_color="white")
        self.email_entry.place(relx=0.1, rely=0.25)
        self.password_entry = ctk.CTkEntry(auth_frame, height=40, width=450,
                                          placeholder_text="********",
                                          placeholder_text_color="#D9D9D9",
                                          font=("inter", 25),
                                          fg_color="#3B3B3B",
                                          text_color="white")
        self.password_entry.place(relx=0.1, rely=0.4)

        #кнопки
        auth_image_btn = ctk.CTkImage(dark_image=Image.open("screens/auth_gradient_button.png"), size=(220, 70))

        ctk.CTkButton(auth_frame, text="", image=auth_image_btn, height=70, width=220,
                                 fg_color="transparent", hover=False,
                                 command=self.login).place(rely=0.67, relx=0.3)
        ctk.CTkButton(auth_frame, text="Зарегистрироваться", width=160, command=self.register).place(rely=0.60, relx=0.35)

        self.msg = ctk.CTkLabel(self, text="", text_color="#ff6666")
        self.msg.pack()

    def register(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        if not email or not password:
            self.msg.configure(text="Введите email и пароль")
            return

        hashed = generate_password_hash(password)
        db = SessionLocal()
        try:
            new_user = User(email=email, password_hash=hashed)
            db.add(new_user)
            db.commit()
            self.msg.configure(text="Успешно зарегистрировано", text_color="#66ff66")
        except IntegrityError:
            db.rollback()
            self.msg.configure(text="Пользователь с таким email уже существует")
        finally:
            db.close()

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        if not email or not password:
            self.msg.configure(text="Введите email и пароль")
            return

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if user and check_password_hash(user.password_hash, password):
                self.msg.configure(text="")
                #вызываю callback и передаю user
                self.switch_to_main(user)
            else:
                self.msg.configure(text="Неправильный email или пароль")
        finally:
            db.close()
