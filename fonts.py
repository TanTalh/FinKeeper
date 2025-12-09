import customtkinter as ctk

class AppFonts:
    main = None
    title = None

    @staticmethod
    def init():
        AppFonts.main = ctk.CTkFont(family="inter", size=18)
        AppFonts.title = ctk.CTkFont(family="inter", weight="bold",size=500)
# Это сделано потому что шрифты должны создаваться после запуска CTk()