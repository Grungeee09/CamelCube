import time
import json
import customtkinter as ctk
from typing import Literal
from tkinter import messagebox


class Data:
    def __init__(self) -> None:
        self._check_times()

    def set_new_record(self, new_record: float) -> None:
        self._check_times()

        last_record = self.get_record_now()

        with open("data.json", "w") as file:
            json.dump({
                "record_now": {"time": new_record, "code": hash(new_record)},
                "record_before": {"time": last_record, "code": hash(last_record)}
            }, file, indent=4)

    def get_record_now(self) -> float:
        self._check_times()

        with open("data.json", "r") as file:
            return json.load(file)["record_now"]["time"]

    @staticmethod
    def _check_file() -> None:
        try:
            with open("data.json", "r") as file:
                data: dict = json.load(file)
            _, _, _, _ = (data["record_now"]["time"], data["record_now"]["code"],
                          data["record_before"]["time"], data["record_before"]["code"])
        except (json.JSONDecodeError, FileNotFoundError, KeyError):
            with open("data.json", "w") as file:
                json.dump({
                    "record_now": {"time": None, "code": hash(None)},
                    "record_before": {"time": None, "code": hash(None)}}, file, indent=4)

    def _check_times(self) -> None:
        self._check_file()

        with open("data.json") as file:
            data: dict = json.load(file)

        if hash(data["record_now"]["time"]) != data["record_now"]["code"]:
            data["record_now"] = {"time": None, "code": hash(None)}

        if hash(data["record_before"]["time"]) != data["record_before"]["code"]:
            data["record_before"] = {"time": None, "code": hash(None)}

        with open("data.json", "w") as file:
            json.dump(data, file, indent=4)


class Root(ctk.CTk):
    def __init__(self) -> None:
        self.data = Data()

        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.title("CamelCube")
        self.geometry("325x300")
        self.resizable(False, False)

        self._init_main_menu()

    def _init_main_menu(self) -> None:
        self.timer_btn = ctk.CTkButton(self, text="Solve timer", font=("Bold", 20), height=275, corner_radius=15,
                                       command=lambda: self._on_choose_option("asm"))
        self.timer_btn.pack(side=ctk.LEFT, padx=10, pady=10)

        self.solver_btn = ctk.CTkButton(self, text="Cube solver", font=("Times new roman", 20), height=275,
                                        corner_radius=15, command=lambda: self._on_choose_option("solve"))
        self.solver_btn.pack(side=ctk.RIGHT, padx=10, pady=10)

    def _init_timer_menu(self) -> None:
        self.time_label = ctk.CTkLabel(self, text="Hold down space to start...", font=("Bold", 25))
        self.time_label.pack(pady=(120, 0))

        self.timer = 0
        self._reset_timer(False, True)

    def _on_choose_option(self, option: Literal["solve", "asm"]) -> None:
        match option:
            case "solve":
                messagebox.showinfo("Info", "This feature is in develop :)")
            case "asm":
                self._hide_main_menu()
                self._init_timer_menu()

    def _hide_main_menu(self) -> None:
        timer_text = self.timer_btn.cget("text")
        solver_text = self.solver_btn.cget("text")

        for i in range(11, -1, -1):
            self.timer_btn.configure(text=timer_text[:i])
            self.solver_btn.configure(text=solver_text[:i])
            self.update()
            self.after(10)

        for i in range(15, -1, -1):
            self.timer_btn.configure(corner_radius=i)
            self.solver_btn.configure(corner_radius=i)
            self.update()
            self.after(10)

        for _ in range(46):
            self.timer_btn.configure(height=self.timer_btn.cget("height") - 6.5)
            self.solver_btn.configure(height=self.timer_btn.cget("height") - 6.5)
            self.update()

        self.timer_btn.forget()
        self.solver_btn.forget()
        self.update()

        self.after(500)

    def _start_timer(self, _=None) -> None:
        self.unbind("<KeyRelease>")
        self.bind("<KeyPress-space>", self._stop_timer)

        self.last_time = time.time()
        while not self.req_to_stop_timer:
            self.timer += time.time() - self.last_time
            self.timer = round(self.timer, 3)
            self.time_label.configure(text=f"{self.timer:.3f}")

            self.last_time = time.time()
            self.update()
            self.after(10)

    def _stop_timer(self, _=None) -> None:
        self.req_to_stop_timer = True
        self.unbind("<KeyPress-space>")

        for i in range(1, 30, 3):
            self.time_label.forget()
            self.time_label.pack(pady=(120 - i, 10))
            self.update()
            self.after(15)

        self.count_frame = ctk.CTkFrame(self, height=40, width=250)
        self.count_frame.pack_propagate(False)
        self.count_frame.pack()

        self.count_btn = ctk.CTkButton(self.count_frame, text="count", width=100,
                                       command=lambda: self._reset_timer(True))
        self.count_btn.pack(side=ctk.LEFT, padx=10)

        self.skip_btn = ctk.CTkButton(self.count_frame, text="skip", width=100,
                                      command=lambda: self._reset_timer(False))
        self.skip_btn.pack(side=ctk.RIGHT, padx=10)

    def _reset_timer(self, count: bool, on_start: bool = False) -> None:
        if not on_start:
            self.count_frame.forget()

            for i in range(1, 30, 3):
                self.time_label.forget()
                self.time_label.pack(pady=(90 + i, 10))
                self.update()
                self.after(15)

            if count and (self.data.get_record_now() is None or self.timer < self.data.get_record_now()):
                self.data.set_new_record(self.timer)
                self.best_time_label.configure(text=f"Best time: {self.timer}")
        else:
            record_now = self.data.get_record_now()
            self.best_time_label = ctk.CTkLabel(self, text=f"Best time: {record_now if record_now is not None else ""}")
            self.best_time_label.pack(pady=10, side=ctk.BOTTOM)

        self.req_to_stop_timer = False
        self.timer = 0

        self.time_label.configure(text="Hold down space to start...")
        self.bind("<KeyRelease>", self._start_timer)
        self.bind("<KeyPress-space>", lambda x: self.time_label.configure(text=f"{self.timer:.3f}"))


if __name__ == '__main__':
    Root().mainloop()
