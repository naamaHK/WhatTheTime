"""
🕐 WhatTheTime - מַה הַשָּׁעָה? 🕐
A fun clock-reading game for kids!
"""

import tkinter as tk
import random
import math
import subprocess


# ---------------------------------------------------------------------------
# Sound helpers (Mac: afplay with built-in system sounds)
# ---------------------------------------------------------------------------

def play_sound(sound_type):
    """Play a system sound. sound_type: 'success' or 'fail'"""
    sounds = {
        "success": "/System/Library/Sounds/Funk.aiff",
        "fail":    "/System/Library/Sounds/Basso.aiff",
    }
    path = sounds.get(sound_type)
    if path:
        try:
            subprocess.Popen(["afplay", path])
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Hebrew time-to-spoken-text conversion (with niqqud)
# ---------------------------------------------------------------------------

HOURS_HEB = {
    1:  "אַחַת",
    2:  "שְׁתַּיִם",
    3:  "שָׁלֹשׁ",
    4:  "אַרְבַּע",
    5:  "חָמֵשׁ",
    6:  "שֵׁשׁ",
    7:  "שֶׁבַע",
    8:  "שְׁמֹנֶה",
    9:  "תֵּשַׁע",
    10: "עֶשֶׂר",
    11: "אַחַת עֶשְׂרֵה",
    12: "שְׁתֵּים עֶשְׂרֵה",
}

# All minute numbers — feminine form (used with דקות)
MINUTES_HEB = {
    5:  "חָמֵשׁ",
    10: "עֶשֶׂר",
    20: "עֶשְׂרִים",
    25: "עֶשְׂרִים וְחָמֵשׁ",
}


def time_to_hebrew(hour, minute):
    """Return how this time is spoken aloud in Hebrew, with niqqud."""
    h = HOURS_HEB[hour]
    next_hour = HOURS_HEB[(hour % 12) + 1]

    if minute == 0:
        return h
    elif minute == 15:
        return f"{h} וָרֶבַע"
    elif minute == 30:
        return f"{h} וָחֵצִי"
    elif minute == 45:
        return f"רֶבַע לְ{next_hour}"
    elif minute <= 25:
        # X past the hour — feminine number + דקות
        m = MINUTES_HEB[minute]
        return f"{h} וְ{m} דַּקּוֹת"
    else:
        # 35, 40, 50, 55 → count back from next hour — feminine + דקות
        back = 60 - minute
        m = MINUTES_HEB[back]
        return f"{m} דַּקּוֹת לְ{next_hour}"


ALL_TIMES = [(h, m) for h in range(1, 13) for m in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]]

BG        = "#E8F4FD"
BTN_BLUE  = "#2980B9"
BTN_GREEN = "#27AE60"
BTN_RED   = "#E74C3C"
DARK      = "#2C3E50"
FONT_TITLE = ("Arial Rounded MT Bold", 28, "bold")
FONT_HEB   = ("Arial", 16, "bold")
FONT_SMALL = ("Arial", 13)

PRAISES = [
    "🎉 כׇּל הַכָּבוֹד! עֲנִיתֶם נָכוֹן! אַתֶּם מַדְהִימִים! 🌟",
    "⭐ יָפֶה מְאֹד! קְרָאתֶם אֶת הַשָּׁעוֹן נָכוֹן! 🎊",
    "🏆 וָאוּ! נָכוֹן לְגַמְרֵי! אַתֶּם גְּאוֹנִים! 🎉",
    "🌈 מְצֻיָּן! כׇּל הַכָּבוֹד לָכֶם! ⭐",
    "🎯 נָכוֹן! אַתֶּם מַמָּשׁ טוֹבִים בָּזֶה! 🥳",
]


# ---------------------------------------------------------------------------
# Shared clock-drawing utility
# ---------------------------------------------------------------------------

def draw_clock(canvas, hour, minute, cx=175, cy=175, r=155):
    canvas.delete("all")

    # Shadow
    canvas.create_oval(cx-r+6, cy-r+6, cx+r+6, cy+r+6, fill="#BDC3C7", outline="")
    # Face
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="white", outline=DARK, width=4)

    # Tick marks
    for i in range(60):
        angle = math.radians(i * 6 - 90)
        if i % 5 == 0:
            ir = r - 14; w = 2
        else:
            ir = r - 8;  w = 1
        x1 = cx + ir * math.cos(angle); y1 = cy + ir * math.sin(angle)
        x2 = cx + (r-4) * math.cos(angle); y2 = cy + (r-4) * math.sin(angle)
        canvas.create_line(x1, y1, x2, y2, fill="#95A5A6", width=w)

    # Numbers
    for i in range(1, 13):
        angle = math.radians(i * 30 - 90)
        nr = r - 26
        nx = cx + nr * math.cos(angle); ny = cy + nr * math.sin(angle)
        canvas.create_text(nx, ny, text=str(i), font=("Arial", 14, "bold"), fill=DARK)

    # Hour hand
    ha = math.radians((hour % 12) * 30 + minute * 0.5 - 90)
    hx = cx + r * 0.5 * math.cos(ha); hy = cy + r * 0.5 * math.sin(ha)
    canvas.create_line(cx, cy, hx, hy, fill=DARK, width=8, capstyle="round")

    # Minute hand
    ma = math.radians(minute * 6 - 90)
    mx = cx + r * 0.75 * math.cos(ma); my = cy + r * 0.75 * math.sin(ma)
    canvas.create_line(cx, cy, mx, my, fill=BTN_RED, width=5, capstyle="round")

    # Centre dot
    canvas.create_oval(cx-8, cy-8, cx+8, cy+8, fill=DARK, outline="white", width=2)


# ---------------------------------------------------------------------------
# Mode-selection screen
# ---------------------------------------------------------------------------

class ModeSelectScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("🕐 מַה הַשָּׁעָה? 🕐")
        self.root.geometry("1100x850")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self._build()

    def _build(self):
        self.frame = tk.Frame(self.root, bg=BG)
        self.frame.pack(expand=True, fill="both")

        tk.Label(self.frame, text="🕐 מַה הַשָּׁעָה? 🕐",
                 font=FONT_TITLE, bg=BG, fg=DARK).pack(pady=(70, 10))

        tk.Label(self.frame, text="בְּחַר מֵאֵיזֶה מִשְׂחָק תַּתְחִיל:",
                 font=FONT_HEB, bg=BG, fg="#7F8C8D").pack(pady=(0, 40))

        btn_cfg = dict(font=("Arial", 18, "bold"), fg=DARK,
                       padx=30, pady=20, relief="raised", bd=4,
                       cursor="hand2", width=22)

        tk.Button(self.frame, text="✏️  כְּתֹב אֶת הַשָּׁעָה",
                  bg="#AED6F1", command=self._start_mode1, **btn_cfg).pack(pady=10)

        tk.Button(self.frame, text="🔘  בְּחַר אֶת הַשָּׁעָה",
                  bg="#A9DFBF", command=self._start_mode2, **btn_cfg).pack(pady=10)

    def _clear(self):
        self.frame.destroy()

    def _start_mode1(self):
        self._clear()
        Mode1Game(self.root, back_cb=self._rebuild)

    def _start_mode2(self):
        self._clear()
        Mode2Game(self.root, back_cb=self._rebuild)

    def _rebuild(self):
        self._build()



# ---------------------------------------------------------------------------
# Scrollable frame helper
# ---------------------------------------------------------------------------

def make_scrollable(root):
    """Return (outer_frame, inner_frame, canvas).
    Pack outer_frame; put all content into inner_frame."""
    outer = tk.Frame(root, bg=BG)
    outer.pack(expand=True, fill="both")

    canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
    scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", expand=True, fill="both")

    inner = tk.Frame(canvas, bg=BG)
    win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(win_id, width=canvas.winfo_width())

    inner.bind("<Configure>", _on_configure)
    canvas.bind("<Configure>", _on_configure)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    return outer, inner, canvas


# ---------------------------------------------------------------------------
# Mode 1 – Write the time
# ---------------------------------------------------------------------------

class Mode1Game:
    MAX_GUESSES = 3

    def __init__(self, root, back_cb):
        self.root = root
        self.root.geometry("1100x1000")
        self.back_cb = back_cb
        self.current_hour = 0
        self.current_minute = 0
        self.guesses_left = self.MAX_GUESSES
        self._build()
        self.new_time()

    def _build(self):
        self._outer, self.frame, self._canvas = make_scrollable(self.root)

        # Top bar
        top = tk.Frame(self.frame, bg=BG)
        top.pack(fill="x", padx=15, pady=(15, 0))
        tk.Button(top, text="← חֲזֹר לַתַּפְרִיט", font=FONT_SMALL,
                  bg="#ECF0F1", fg=DARK, relief="flat", cursor="hand2",
                  command=self._back).pack(side="left")

        tk.Label(self.frame, text="🕐 מַה הַשָּׁעָה? 🕐",
                 font=FONT_TITLE, bg=BG, fg=DARK).pack(pady=(5, 2))
        tk.Label(self.frame,
                 text="הִסְתַּכְּלוּ עַל הַשָּׁעוֹן וּכְתְבוּ אֶת הַשָּׁעָה!",
                 font=FONT_SMALL, bg=BG, fg="#7F8C8D").pack(pady=(0, 2))

        self.guesses_label = tk.Label(self.frame, text="", font=FONT_SMALL,
                                      bg=BG, fg=DARK)
        self.guesses_label.pack(pady=(0, 8))

        # Clock
        cf = tk.Frame(self.frame, bg=BG); cf.pack()
        self.canvas = tk.Canvas(cf, width=350, height=350, bg=BG, highlightthickness=0)
        self.canvas.pack()

        # Inputs
        inp = tk.Frame(self.frame, bg=BG); inp.pack(pady=15)

        mf = tk.Frame(inp, bg=BG); mf.pack(side="left", padx=25)
        tk.Label(mf, text="דַּקּוֹת", font=FONT_HEB, bg=BG, fg=BTN_BLUE).pack()
        self.minute_entry = tk.Entry(mf, font=("Arial", 22, "bold"), width=4,
                                     justify="center", bd=3, relief="groove",
                                     bg="white", fg="#1A1A1A", insertbackground="#1A1A1A")
        self.minute_entry.pack(pady=5)
        self.minute_entry.bind("<Return>", lambda e: self.check_answer())

        hf = tk.Frame(inp, bg=BG); hf.pack(side="left", padx=25)
        tk.Label(hf, text="שָׁעָה", font=FONT_HEB, bg=BG, fg=BTN_BLUE).pack()
        self.hour_entry = tk.Entry(hf, font=("Arial", 22, "bold"), width=4,
                                   justify="center", bd=3, relief="groove",
                                   bg="white", fg="#1A1A1A", insertbackground="#1A1A1A")
        self.hour_entry.pack(pady=5)
        self.hour_entry.bind("<Return>", lambda e: self.check_answer())
        self.hour_entry.bind("<KeyRelease>", self._on_hour_key)

        # Buttons
        bf = tk.Frame(self.frame, bg=BG); bf.pack(pady=8)
        tk.Button(bf, text="✅ בְּדֹק!", font=FONT_HEB, bg="#A9DFBF", fg=DARK,
                  padx=25, pady=10, relief="raised", bd=3, cursor="hand2",
                  command=self.check_answer).pack(side="left", padx=8)
        tk.Button(bf, text="🔄 שָׁעָה חֲדָשָׁה", font=FONT_HEB, bg="#AED6F1", fg=DARK,
                  padx=25, pady=10, relief="raised", bd=3, cursor="hand2",
                  command=self.new_time).pack(side="left", padx=8)
        self.read_btn = tk.Button(bf, text="🔊 הַקְרֵא", font=FONT_HEB, bg="#D7BDE2", fg=DARK,
                                  padx=18, pady=10, relief="raised", bd=3, cursor="hand2",
                                  state="disabled", command=self.read_aloud)
        self.read_btn.pack(side="left", padx=8)

        self.feedback = tk.Label(self.frame, text="", font=("Arial", 20, "bold"),
                                 bg=BG, fg=BTN_GREEN, wraplength=700)
        self.feedback.pack(pady=15)

    def _on_hour_key(self, event):
        if event.keysym in ("BackSpace", "Delete", "Return", "Tab"):
            return
        val = self.hour_entry.get().strip()
        if not val:
            return
        if len(val) >= 2 or (len(val) == 1 and val in '3456789'):
            self.minute_entry.focus()

    def new_time(self):
        self.current_hour, self.current_minute = random.choice(ALL_TIMES)
        self.guesses_left = self.MAX_GUESSES
        draw_clock(self.canvas, self.current_hour, self.current_minute,
                   cx=175, cy=175, r=155)
        self.hour_entry.config(state="normal")
        self.minute_entry.config(state="normal")
        self.hour_entry.delete(0, tk.END)
        self.minute_entry.delete(0, tk.END)
        self.read_btn.config(state="disabled")
        self.feedback.config(text="", fg=BTN_GREEN)
        self._update_guesses_label()
        self.hour_entry.focus()

    def check_answer(self):
        if self.guesses_left <= 0:
            return
        try:
            uh = int(self.hour_entry.get().strip())
            um = int(self.minute_entry.get().strip())
        except ValueError:
            self.feedback.config(text="❓ אָנָּא הַכְנֵס מִסְפָּרִים בִּלְבַד!", fg="#E67E22")
            return

        if uh == self.current_hour and um == self.current_minute:
            play_sound("success")
            self.guesses_left = 0
            self._update_guesses_label()
            self.feedback.config(text=random.choice(PRAISES), fg=BTN_GREEN)
            self.hour_entry.config(state="disabled")
            self.minute_entry.config(state="disabled")
            self.read_btn.config(state="normal", bg="#8E44AD", fg=DARK)
        else:
            self.guesses_left -= 1
            play_sound("fail")
            self._update_guesses_label()
            self._shake()
            if self.guesses_left == 0:
                correct_text = time_to_hebrew(self.current_hour, self.current_minute)
                self.feedback.config(
                    text=f"😔 לֹא נוֹרָא! הַתְּשׁוּבָה: {self.current_hour}:{self.current_minute:02d}  ·  {correct_text}",
                    fg="#E67E22"
                )
                self.hour_entry.config(state="disabled")
                self.minute_entry.config(state="disabled")
                self.read_btn.config(state="normal", bg="#8E44AD", fg=DARK)
            else:
                self.feedback.config(text="💪 נַסוּ שׁוּב! אַתֶם יְכוֹלִים! 😊", fg=BTN_RED)

    def read_aloud(self):
        """Speak the current clock time in Hebrew using Mac's 'say' command."""
        if self.current_hour == 0:
            return
        text = time_to_hebrew(self.current_hour, self.current_minute)
        try:
            subprocess.Popen(["say", "-v", "Carmit", text])
        except Exception:
            pass

    def _update_guesses_label(self):
        hearts = "❤️" * self.guesses_left + "🖤" * (self.MAX_GUESSES - self.guesses_left)
        self.guesses_label.config(text=f"נִסְיוֹנוֹת: {hearts}")

    def _shake(self):
        x = self.root.winfo_x(); y = self.root.winfo_y()
        for dx in [8, -8, 6, -6, 4, -4, 0]:
            self.root.after(30 * abs(dx), lambda d=dx: self.root.geometry(f"+{x+d}+{y}"))

    def _back(self):
        self._outer.destroy()
        self.root.geometry("1100x850")
        self.back_cb()


# ---------------------------------------------------------------------------
# Mode 2 – Multiple choice (spoken Hebrew time)
# ---------------------------------------------------------------------------

class Mode2Game:
    MAX_GUESSES = 3

    def __init__(self, root, back_cb):
        self.root = root
        self.root.geometry("1100x1000")
        self.back_cb = back_cb
        self.current_hour = 0
        self.current_minute = 0
        self.guesses_left = self.MAX_GUESSES
        self.choice_btns = []
        self._build()
        self.new_question()

    def _build(self):
        self._outer, self.frame, self._canvas = make_scrollable(self.root)

        # Top bar
        top = tk.Frame(self.frame, bg=BG)
        top.pack(fill="x", padx=15, pady=(15, 0))
        tk.Button(top, text="← חֲזֹר לַתַּפְרִיט", font=FONT_SMALL,
                  bg="#ECF0F1", fg=DARK, relief="flat", cursor="hand2",
                  command=self._back).pack(side="left")

        tk.Label(self.frame, text="🕐 מַה הַשָּׁעָה? 🕐",
                 font=FONT_TITLE, bg=BG, fg=DARK).pack(pady=(5, 2))
        tk.Label(self.frame, text="בְּחַר אֶת הַשָּׁעָה הַנְּכוֹנָה:",
                 font=FONT_SMALL, bg=BG, fg="#7F8C8D").pack(pady=(0, 8))

        # Guess counter
        self.guesses_label = tk.Label(self.frame, text="", font=FONT_SMALL,
                                      bg=BG, fg=DARK)
        self.guesses_label.pack()

        # Clock
        cf = tk.Frame(self.frame, bg=BG); cf.pack()
        self.canvas = tk.Canvas(cf, width=350, height=350, bg=BG, highlightthickness=0)
        self.canvas.pack()

        # 4 choice buttons
        choices_outer = tk.Frame(self.frame, bg=BG)
        choices_outer.pack(pady=10)

        self.choice_frame = tk.Frame(choices_outer, bg=BG)
        self.choice_frame.pack()

        for i in range(4):
            btn = tk.Button(self.choice_frame, text="", font=("Arial", 17, "bold"),
                            bg="white", fg=DARK, width=26, pady=12,
                            relief="raised", bd=3, cursor="hand2",
                            command=lambda idx=i: self._guess(idx))
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=6)
            self.choice_btns.append(btn)

        # New question + read-aloud buttons
        bottom_bf = tk.Frame(self.frame, bg=BG)
        bottom_bf.pack(pady=8)
        tk.Button(bottom_bf, text="🔄 שָׁאֵלָה חֲדָשָׁה", font=FONT_HEB,
                  bg="#AED6F1", fg=DARK, padx=25, pady=10,
                  relief="raised", bd=3, cursor="hand2",
                  command=self.new_question).pack(side="left", padx=8)
        self.read_btn = tk.Button(bottom_bf, text="🔊 הַקְרֵא", font=FONT_HEB,
                                  bg="#D7BDE2", fg=DARK, padx=18, pady=10,
                                  relief="raised", bd=3, cursor="hand2",
                                  state="disabled", command=self.read_aloud)
        self.read_btn.pack(side="left", padx=8)

        self.feedback = tk.Label(self.frame, text="", font=("Arial", 18, "bold"),
                                 bg=BG, fg=BTN_GREEN, wraplength=650)
        self.feedback.pack(pady=10)

    def new_question(self):
        self.current_hour, self.current_minute = random.choice(ALL_TIMES)
        self.guesses_left = self.MAX_GUESSES
        self.feedback.config(text="")
        self.read_btn.config(state="disabled", bg="#D7BDE2")
        draw_clock(self.canvas, self.current_hour, self.current_minute,
                   cx=175, cy=175, r=155)
        self._set_choices()
        self._reset_buttons()
        self._update_guesses_label()

    def _set_choices(self):
        """Pick 1 correct + 3 distractor times, shuffle, store."""
        correct = (self.current_hour, self.current_minute)
        pool = [t for t in ALL_TIMES if t != correct]
        distractors = random.sample(pool, 3)
        options = [correct] + distractors
        random.shuffle(options)
        self.correct_idx = options.index(correct)
        self.options = options

        for i, (h, m) in enumerate(options):
            self.choice_btns[i].config(text=time_to_hebrew(h, m),
                                       bg="white", fg=DARK, state="normal")

    def _reset_buttons(self):
        for btn in self.choice_btns:
            btn.config(bg="white", fg=DARK, state="normal")

    def _update_guesses_label(self):
        hearts = "❤️" * self.guesses_left + "🖤" * (self.MAX_GUESSES - self.guesses_left)
        self.guesses_label.config(text=f"נִסְיוֹנוֹת: {hearts}")

    def _guess(self, idx):
        if idx == self.correct_idx:
            play_sound("success")
            self.choice_btns[idx].config(bg=BTN_GREEN, fg=DARK)
            self.feedback.config(text=random.choice(PRAISES), fg=BTN_GREEN)
            self.read_btn.config(state="normal", bg="#8E44AD", fg=DARK)
            # Disable all choice buttons after correct
            for btn in self.choice_btns:
                btn.config(state="disabled")
        else:
            self.guesses_left -= 1
            play_sound("fail")
            self.choice_btns[idx].config(bg=BTN_RED, fg="white", state="disabled")
            self._update_guesses_label()
            self._shake()

            if self.guesses_left == 0:
                # Show the correct answer as text (bg color may not render on Mac)
                correct_text = time_to_hebrew(self.current_hour, self.current_minute)
                self.feedback.config(
                    text=f"😔 לֹא נוֹרָא! התְּשׁוּבָה הַנְּכוֹנָה: {correct_text}",
                    fg="#E67E22"
                )
                self.choice_btns[self.correct_idx].config(
                    state="normal", bg=BTN_GREEN, fg=DARK
                )
                for i, btn in enumerate(self.choice_btns):
                    if i != self.correct_idx:
                        btn.config(state="disabled")
                self.read_btn.config(state="normal", bg="#8E44AD", fg=DARK)
            else:
                self.feedback.config(
                    text="💪 נַסוּ שׁוּב! אַתֶם יְכוֹלִים! 😊",
                    fg=BTN_RED
                )


    def read_aloud(self):
        """Speak the current clock time in Hebrew using Mac's 'say' command."""
        if self.current_hour == 0:
            return
        text = time_to_hebrew(self.current_hour, self.current_minute)
        try:
            subprocess.Popen(["say", "-v", "Carmit", text])
        except Exception:
            pass

    def _shake(self):
        x = self.root.winfo_x(); y = self.root.winfo_y()
        for dx in [8, -8, 6, -6, 4, -4, 0]:
            self.root.after(30 * abs(dx), lambda d=dx: self.root.geometry(f"+{x+d}+{y}"))

    def _back(self):
        self._outer.destroy()
        self.root.geometry("1100x850")
        self.back_cb()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    root = tk.Tk()
    ModeSelectScreen(root)
    root.mainloop()


if __name__ == "__main__":
    main()
