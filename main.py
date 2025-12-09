import customtkinter as ctk
from database.db import engine, Base
Base.metadata.create_all(bind=engine)
from screens.registerWindow import RegisterFrame
from screens.loginWindow import LoginFrame
from screens.mainWindow import MainFrame


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FinKeeper")
        self.current_frame = None
        self.main_font = ctk.CTkFont(family="inter", size=18)
        self.title_font = ctk.CTkFont(family="inter", weight="bold", size=32)

        self.after(0, lambda: self.center_window_to_display(1280, 720))

        self.after(10, self.show_register)
        self.current_frame = None


    def center_window_to_display(self, width: int, height: int):
        self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None


    def show_login(self):
        self.clear_frame()
        self.current_frame = LoginFrame(self, self.on_login_success)

    def show_register(self):
        self.clear_frame()
        self.current_frame = RegisterFrame(self, self.on_login_success)

    def on_login_success(self, user):
        self.state("zoomed")
        self.clear_frame()
        self.current_frame = MainFrame(self, user, self.show_login)





if __name__ == "__main__":
    app = App()
    app.mainloop()
