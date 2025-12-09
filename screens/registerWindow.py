import customtkinter as ctk
import pywinstyles
from PIL import Image
from database.db import SessionLocal
from database.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

class RegisterFrame(ctk.CTkFrame):
    def __init__(self, master, switch_to_main_callback):
        super().__init__(master)
        self.switch_to_main = switch_to_main_callback

        self.pack(fill="both", expand=True)

        register_frame = ctk.CTkFrame(self, height=500, width=610, fg_color="#2c2c2c", corner_radius=55)
        register_frame.pack_propagate(False)
        register_frame.place(rely=0.5, relx=0.5, anchor="center")
        # изображения
        register_image = ctk.CTkImage(dark_image=Image.open("images/register_gradient_button.png"), size=(405, 70))
        reg_title_image = ctk.CTkImage(dark_image=Image.open("images/register_title.png"), size=(209,45))



        self.login_entry = ctk.CTkEntry(register_frame, height=40, width=450,
                                        placeholder_text="Enter login",
                                        placeholder_text_color="#d9d9d9",
                                        font=ctk.CTkFont(family="inter", size=25),
                                        fg_color="#3b3b3b",
                                        text_color="white")
        self.login_entry.place(relx=0.1, rely=0.25)

        self.password_entry = ctk.CTkEntry(register_frame,height=40,width=450,
                                           placeholder_text="********",
                                           placeholder_text_color="#d9d9d9",
                                           font=ctk.CTkFont(family="inter",size=25),
                                           fg_color="#3b3b3b",
                                           text_color="white")
        self.password_entry.place(relx=0.1, rely=0.4)

        # кнопки
        self.reg_btn = ctk.CTkButton(register_frame, text="",
                                     width=100, height=50,
                                     image=reg_title_image,
                                     fg_color="transparent",
                                     hover=False)
        self.reg_btn.place(rely=0.06, relx=0.55)
        self.auth_btn = ctk.CTkButton(register_frame, text="Авторизация",
                                      width=100, height=50,
                                      font=master.title_font,
                                      text_color="white",
                                      hover=False,
                                      fg_color="transparent",
                                      command=master.show_login)
        self.auth_btn.place(rely=0.06, relx=0.1)
        pywinstyles.set_opacity(self.auth_btn.winfo_id(), value=0.25, color="#000001")

        ctk.CTkButton(register_frame, text="", image=register_image,
                      width=405,height=70,
                      fg_color="transparent", hover=False,
                      command=self.register).place(rely=0.67, relx=0.15)

        self.msg = ctk.CTkLabel(self, text="", text_color="#ff6666")
        self.msg.pack()

    def register(self):
        email = self.login_entry.get().strip()
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