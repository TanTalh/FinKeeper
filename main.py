import customtkinter as ctk
from database.db import engine, Base
from database import models


Base.metadata.create_all(bind=engine)

from screens.loginWindow import LoginFrame
from screens.mainWindow import MainFrame

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1280x720")
        self.title("FinKeeper")

        self.current_frame = None
        self.show_login()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None

    def show_login(self):
        self.geometry("1280x720")
        self.state("normal")

        self.clear_frame()
        self.current_frame = LoginFrame(self, self.on_login_success)

    def on_login_success(self, user):
        self.geometry("1920x1080")
        self.state("zoomed")

        self.clear_frame()
        self.current_frame = MainFrame(self, user, self.show_login)

if __name__ == "__main__":
    app = App()
    app.mainloop()
