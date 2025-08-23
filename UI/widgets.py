import multiprocessing

import customtkinter as ctk
from PIL import Image

from core.utils.loader import PATHS_CONFIG


class PopUp(ctk.CTkToplevel):
    def __init__(self, master=None, on_submit=None, **kwargs):
        super().__init__(master, **kwargs)
        self.geometry("200x100")
        self.title("pop up")
        subtitle = ctk.CTkLabel(
            self, text="Enter your name", width=130, height=30, font=("Arial", 18)
        )
        subtitle.pack(side="top")
        self.entry = ctk.CTkEntry(self, width=150, height=50)
        self.entry.pack(pady=20, side="bottom")

        self.on_submit = on_submit

        self.entry.bind("<Return>", self.get_name)

    def get_name(self, event=None):
        name = self.entry.get()
        if self.on_submit:
            self.on_submit(name)
        self.destroy()


class ProgressPopUp(ctk.CTkToplevel):
    def __init__(self, master, total, queue, **kwargs):
        super().__init__(master, **kwargs)
        self.geometry("450x215")
        self.title("Running analysis")

        self.progress = ctk.CTkProgressBar(
            self, width=400, height=20, progress_color="red"
        )
        self.progress.pack(pady=10)
        self.progress.set(0)
        self.label = ctk.CTkLabel(self, text="0%", font=("Arial", 14))
        self.label.pack(pady=(10, 5))
        self.current_song_name = ctk.CTkLabel(
            self, text="Initializing TensorFlow", font=("Arial", 14), width=430
        )
        self.current_song_name.pack(pady=(0, 10))
        self.total = total
        self.current = 0
        self.current_fraction = 0
        self.queue = queue
        self.last_song_name = None

        gear_frame = ctk.CTkFrame(self, width=200, height=150, fg_color="transparent")
        gear_frame.pack(side="right", fill="y", padx=10)

        self.original_img = Image.open(PATHS_CONFIG["ui_images"]["loading_gear"])

        self.spinning_img = ctk.CTkImage(
            light_image=self.original_img, dark_image=self.original_img, size=(64, 64)
        )
        self.img_label = ctk.CTkLabel(gear_frame, text="", image=self.spinning_img)
        self.img_label.pack(pady=(20, 0))
        self.angle = 0

        self.rotate_image()
        self.check_queue()

        self.animate_dots()

    def rotate_image(self):
        self.angle = (self.angle + 10) % 360
        rotated = self.original_img.rotate(self.angle)
        self.spinning_img = ctk.CTkImage(
            light_image=rotated, dark_image=rotated, size=(64, 64)
        )
        self.img_label.configure(image=self.spinning_img)
        self.after(50, self.rotate_image)

    def check_queue(self):
        try:
            while not self.queue.empty():
                msg = self.queue.get_nowait()
                if msg[0] == "progress":
                    song_name, advance = msg[1], msg[2]
                    self.update_progress(song_name=song_name, advance=advance)
                elif msg[0] == "done":
                    self.progress.set(1.0)
                    self.label.configure(text="100%")
                    self.current_song_name.configure(text="Done!")
                    self.after(1500, self.destroy)
        except Exception as e:
            print("Queue error:", e)
        self.after(100, self.check_queue)

    def animate_dots(self):
        if not isinstance(self.last_song_name, int):
            self.dot_index = getattr(self, "dot_index", 0)
            self.dot_index += 1
            dots = "." * ((self.dot_index % 3) + 1)

            current_text = self.current_song_name.cget("text")
            base_text = current_text.split(".")[0]
            self.current_song_name.configure(text=f"{base_text}{dots}")

        self.after(500, self.animate_dots)

    def update_progress(self, song_name=None, advance=True):
        self.last_song_name = song_name

        if isinstance(song_name, str):
            self.current_song_name.configure(text=f"Analyzing {song_name}")
        elif isinstance(song_name, int):
            self.current_song_name.configure(
                text="An error occured during the process of this song."
            )
        else:
            self.current_song_name.configure(text="Downloading next song")
        if advance:
            self.current += 1
            target_fraction = self.current / self.total
            self.animate_progress(target_fraction)

    def animate_progress(self, target_fraction):
        if self.current_fraction >= target_fraction:
            return

        increment = 0.01
        self.current_fraction = min(self.current_fraction + increment, target_fraction)
        self.progress.set(self.current_fraction)

        # Couleurs dynamiques
        if self.current_fraction < 0.5:
            self.progress.configure(progress_color="red")
        elif self.current_fraction < 0.8:
            self.progress.configure(progress_color="orange")
        else:
            self.progress.configure(progress_color="green")

        self.label.configure(text=f"{int(self.current_fraction*100)}%")

        self.after(0, lambda: self.animate_progress(target_fraction))


def worker_main(name, queue):
    import core.song_pipeline as song_pipeline

    def progress_callback(song_name, advance):
        queue.put(("progress", song_name, advance))

    song_pipeline.main(name, progress_callback=progress_callback)
    queue.put(("done",))


class SongDump(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("700x500")

        title = ctk.CTkLabel(self, text="Upload songs")
        title.pack(padx=20, pady=20)
        textbox = ctk.CTkTextbox(self, width=400, height=500)
        textbox.pack(pady=10, side="left")

        dump_button = ctk.CTkButton(
            self,
            width=100,
            height=80,
            text="Upload",
            command=lambda: self.dumpURLs(textbox),
        )
        dump_button.pack(pady=30, padx=10)

        self.pop_up_window = None
        self.progress_pop_up_window = None

    def dumpURLs(self, textbox):
        content = textbox.get("1.0", "end-1c")
        if content == "":
            return
        with open(PATHS_CONFIG["song_requests"], "w", encoding="utf-8") as f:
            f.write(content)
        lines = [line for line in content.split("\n") if line.strip()]
        self.total_songs = len(lines)
        if self.pop_up_window is None or not self.pop_up_window.winfo_exists():
            self.pop_up_window = PopUp(self, on_submit=self.after_pop_up)
        else:
            self.pop_up_window.focus()

    def after_pop_up(self, name: str):
        print("Name fetched from pop-up:", name)
        self.pop_up_window = None
        queue = multiprocessing.Queue()
        self.progress_pop_up_window = ProgressPopUp(self, self.total_songs, queue)

        process = multiprocessing.Process(target=worker_main, args=(name, queue))
        process.start()


class SongPredict(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")

        self.label = ctk.CTkLabel(self, text="Predict the ideal listener")
        self.label.pack(padx=20, pady=20)
