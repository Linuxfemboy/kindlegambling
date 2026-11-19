#!/usr/bin/env python3
"""Roulette-style spin wheel for e-ink (Kindle Alpine chroot). Tap to spin."""

import math
import random
import tkinter as tk


# European roulette order. Edit SLOTS to use your own labels instead.
SLOTS = [
    0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23,
    10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26,
]
RED = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

FRAMES = 28
DELAY_MS = 130
STEP = 360 / len(SLOTS)


def colors(label):
    if label == 0:
        return "#888888", "black"
    if label in RED:
        return "black", "white"
    return "white", "black"


class Wheel:
    def __init__(self, root):
        self.root = root
        self.spinning = False
        self.offset = 0.0
        self.c = tk.Canvas(root, bg="white", highlightthickness=0)
        self.c.pack(fill="both", expand=True)

        root.update()
        w, h = self.c.winfo_width(), self.c.winfo_height()
        self.cx, self.cy = w / 2, h / 2
        self.r = min(w, h) * 0.45
        self.arcs, self.texts = [], []

        box = (
            self.cx - self.r,
            self.cy - self.r,
            self.cx + self.r,
            self.cy + self.r,
        )
        for i, label in enumerate(SLOTS):
            fill, fg = colors(label)
            self.arcs.append(
                self.c.create_arc(
                    box,
                    start=0,
                    extent=STEP,
                    fill=fill,
                    outline="black",
                    width=2,
                )
            )
            self.texts.append(
                self.c.create_text(
                    0,
                    0,
                    text=str(label),
                    fill=fg,
                    font=("DejaVu Sans", int(self.r / 14), "bold"),
                )
            )

        hub = self.r * 0.38
        self.c.create_oval(
            self.cx - hub,
            self.cy - hub,
            self.cx + hub,
            self.cy + hub,
            fill="white",
            outline="black",
            width=4,
        )
        self.result = self.c.create_text(
            self.cx,
            self.cy,
            text="TAP",
            font=("DejaVu Sans", int(self.r / 4), "bold"),
        )

        top = self.cy - self.r
        self.c.create_polygon(
            self.cx - 25,
            top - 40,
            self.cx + 25,
            top - 40,
            self.cx,
            top + 15,
            fill="black",
            outline="white",
            width=2,
        )
        quit_button = tk.Button(root, text="Quit", command=root.destroy)
        quit_button.place(x=10, y=10)

        self.c.bind("<Button-1>", lambda event: self.spin())
        self.draw()

    def draw(self):
        for i in range(len(SLOTS)):
            angle = self.offset + i * STEP
            self.c.itemconfigure(self.arcs[i], start=angle)
            mid = math.radians(angle + STEP / 2)
            radius = self.r * 0.78
            self.c.coords(
                self.texts[i],
                self.cx + radius * math.cos(mid),
                self.cy - radius * math.sin(mid),
            )

    def winner(self):
        # The pointer sits at 90 degrees (top).
        index = int(((90 - self.offset) % 360) // STEP)
        return SLOTS[index]

    def spin(self):
        if self.spinning:
            return

        self.spinning = True
        self.c.itemconfigure(self.result, text="...")
        start = self.offset
        total = random.uniform(5, 9) * 360 + random.uniform(0, 360)
        self.step(0, start, total)

    def step(self, frame, start, total):
        progress = frame / FRAMES
        ease = 1 - (1 - progress) ** 3
        self.offset = (start - total * ease) % 360
        self.draw()

        if frame < FRAMES:
            self.root.after(DELAY_MS, self.step, frame + 1, start, total)
        else:
            winner = self.winner()
            self.c.itemconfigure(self.result, text=str(winner))
            self.spinning = False


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Wheel")
    root.geometry("1072x1448")
    Wheel(root)
    root.mainloop()
