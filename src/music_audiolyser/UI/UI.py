import customtkinter as ctk
from PIL import Image

from ..core.utils.constants import PATHS_CONFIG, UI_CONFIG
from . import widgets


class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry(UI_CONFIG["window_size"])
        self.title(UI_CONFIG["title"])
        ctk.set_appearance_mode(UI_CONFIG["theme"])

        button_frame = ctk.CTkFrame(self, width=500, height=100)
        button_frame.pack(pady=50, padx=50, side="bottom")

        top_frame = ctk.CTkFrame(self, width=700, height=80, fg_color="transparent")
        top_frame.pack(side="top", fill="x", pady=20)

        top_frame.pack_propagate(False)

        title = ctk.CTkLabel(top_frame, text=UI_CONFIG["title"], font=("Arial", 45))
        title.place(relx=0.5, rely=0.5, anchor="center")

        button_settings = ctk.CTkButton(
            top_frame, text="settings", width=70, height=70, command=self.openSettings
        )
        button_settings.place(relx=1.0, rely=0.0, anchor="ne", x=-20)

        main_menu_img = Image.open(PATHS_CONFIG["ui_images"]["main_menu_img"])
        ctk_main_menu_img = ctk.CTkImage(
            light_image=main_menu_img, dark_image=main_menu_img, size=(300, 225)
        )
        img_label = ctk.CTkLabel(self, text="", image=ctk_main_menu_img)
        img_label.pack()

        button_left = ctk.CTkButton(
            button_frame,
            text="Upload songs",
            width=200,
            height=80,
            command=self.openSongDump,
        )
        button_left.pack(pady=0, padx=50, side="left")
        button_right = ctk.CTkButton(
            button_frame,
            text="Predict the ideal listener",
            width=200,
            height=80,
            command=self.openSongPredict,
        )
        button_right.pack(pady=0, padx=50, side="right")

        self.song_dump_window = None
        self.song_predict_window = None
        self.settings_window = None

    def openSongDump(self):
        if self.song_dump_window is None or not self.song_dump_window.winfo_exists():
            self.song_dump_window = widgets.SongDump(self)
        else:
            self.song_dump_window.focus()

    def openSongPredict(self):
        if (
            self.song_predict_window is None
            or not self.song_predict_window.winfo_exists()
        ):
            self.song_predict_window = widgets.SongPredict(self)
        else:
            self.song_predict_window.focus()

    def openSettings(self):

        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = widgets.Settings(self)
        else:
            self.settings_window.focus()
