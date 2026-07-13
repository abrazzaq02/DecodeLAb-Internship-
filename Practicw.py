
import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime
import random
import re
import math



LIGHT_THEME = {
    "name": "light",
    "gradient_top": (0xEA, 0xF6, 0xF1),      # very light mint
    "gradient_bottom": (0xCF, 0xE9, 0xE0),   # slightly deeper mint
    "header_bg": "#1F6F5C",
    "header_fg": "#FFFFFF",
    "panel_bg": "#FFFFFF",
    "user_bubble": "#1F6F5C",
    "user_text": "#FFFFFF",
    "bot_bubble": "#FFFFFF",
    "bot_bubble_border": "#D8E3DF",
    "bot_text": "#1B1B1B",
    "timestamp": "#8A8A8A",
    "input_bg": "#FFFFFF",
    "input_fg": "#1B1B1B",
    "input_border": "#C9D6D1",
    "send_btn_bg": "#1F6F5C",
    "send_btn_fg": "#FFFFFF",
    "clear_btn_bg": "#B23A48",
    "clear_btn_fg": "#FFFFFF",
    "toggle_track_off": "#C9D6D1",
    "toggle_track_on": "#1F6F5C",
    "toggle_knob": "#FFFFFF",
}

DARK_THEME = {
    "name": "dark",
    "gradient_top": (0x15, 0x1E, 0x1C),       # near-black green-tinted
    "gradient_bottom": (0x0B, 0x12, 0x11),    # almost pure black
    "header_bg": "#123D32",
    "header_fg": "#EAF6F1",
    "panel_bg": "#1B2624",
    "user_bubble": "#2FA98C",
    "user_text": "#08120F",
    "bot_bubble": "#243330",
    "bot_bubble_border": "#33453F",
    "bot_text": "#EAF6F1",
    "timestamp": "#7F9A93",
    "input_bg": "#243330",
    "input_fg": "#EAF6F1",
    "input_border": "#33453F",
    "send_btn_bg": "#2FA98C",
    "send_btn_fg": "#08120F",
    "clear_btn_bg": "#C1495A",
    "clear_btn_fg": "#FFFFFF",
    "toggle_track_off": "#33453F",
    "toggle_track_on": "#2FA98C",
    "toggle_knob": "#EAF6F1",
}




BOT_NAME = "Ally"

KNOWLEDGE_BASE = [
    (["hello", "hi ", "hi", "hey", "salam", "assalam", "yo "],
     ["Hello! 👋 How can I help you today?",
      "Hi there! What's on your mind?",
      "Hey! Great to see you here."]),

    (["how are you", "how're you", "how you doing"],
     ["I'm just code, but I'm running perfectly! How about you?",
      "Doing great, thanks for asking! What about you?"]),

    (["your name", "who are you", "what are you"],
     [f"I'm {BOT_NAME}, a rule-based chatbot built with Python and Tkinter."]),

    (["creator", "made you", "developer", "built you", "who built"],
     ["I was built for a Decode Labs Python internship task, using only Tkinter for the GUI."]),

    (["help", "what can you do", "commands", "menu"],
     ["Here's what I can chat about: greetings, my name/creator, time & date, "
      "jokes, motivational quotes, simple math (try '12 * 4 + 3'), and more. "
      "Just type naturally!"]),

    (["time"],
     [lambda: f"The current time is {datetime.now().strftime('%I:%M %p')}."]),

    (["date", "today"],
     [lambda: f"Today's date is {datetime.now().strftime('%B %d, %Y')}."]),

    (["weather"],
     ["I can't check live weather (no internet access in this demo), "
      "but I hope it's nice outside! ☀️"]),

    (["thank", "thanks", "shukriya"],
     ["You're welcome! 😊", "Anytime — happy to help!", "No problem at all!"]),

    (["bye", "goodbye", "exit", "quit", "see you"],
     ["Goodbye! Have a great day. 👋", "See you later! Take care."]),

    (["joke", "funny"],
     ["Why do programmers prefer dark mode? Because light attracts bugs!",
      "Why did the developer go broke? They used up all their cache.",
      "I would tell you a UDP joke, but you might not get it."]),

    (["quote", "motivate", "motivation", "inspire"],
     ["\"The best way to get started is to quit talking and begin doing.\" — Walt Disney",
      "\"Don't watch the clock; do what it does. Keep going.\" — Sam Levenson",
      "\"Success is the sum of small efforts, repeated day in and day out.\" — R. Collier"]),

    (["love you", "i love you"],
     ["Aw, that's sweet! I'm just a program, but I appreciate you. 💚"]),

    (["sad", "upset", "depressed", "unhappy"],
     ["I'm sorry you're feeling that way. I'm just a simple chatbot, but if things "
      "feel heavy, it can really help to talk to someone you trust or a professional."]),

    (["python", "tkinter", "code", "programming"],
     ["This whole chatbot — the window, the gradient background, the chat bubbles, "
      "and my replies — is written in plain Python using the Tkinter library."]),

    (["dark mode", "light mode", "theme"],
     ["Try the toggle switch in the top-right corner of the window — it switches "
      "the whole UI between light and dark themes instantly!"]),
]

FALLBACK_REPLIES = [
    "I'm not sure I understand. Could you rephrase that?",
    "Hmm, I don't have an answer for that yet — try typing 'help' to see what I can do.",
    "I'm just a rule-based demo bot, so that one's outside my knowledge base!",
]


def try_evaluate_math(text: str):
    """
    Safely evaluates simple arithmetic expressions like '12 * 4 + 3'.
    Only digits, spaces, and + - * / ( ) . are allowed — anything else
    is rejected, so this never runs arbitrary/unsafe code.
    """
    cleaned = text.strip()
    if not re.fullmatch(r"[0-9+\-*/().\s]+", cleaned):
        return None
    if not any(ch.isdigit() for ch in cleaned):
        return None
    try:
        result = eval(cleaned, {"__builtins__": {}}, {})
        return f"{cleaned} = {result}"
    except Exception:
        return None


def get_bot_reply(user_text: str) -> str:
    """Main reply engine: math check first, then keyword knowledge base, then fallback."""
    text = user_text.lower().strip()
    if not text:
        return "Say something and I'll try to respond!"

    math_result = try_evaluate_math(user_text)
    if math_result:
        return f"🧮 {math_result}"

    for keywords, replies in KNOWLEDGE_BASE:
        if any(keyword in text for keyword in keywords):
            choice = random.choice(replies)
            return choice() if callable(choice) else choice

    return random.choice(FALLBACK_REPLIES)




def _interpolate_color(c1: tuple, c2: tuple, t: float) -> str:
    """Blends two (r, g, b) colors together. t=0 -> c1, t=1 -> c2."""
    r = int(c1[0] + (c2[0] - c1[0]) * t)
    g = int(c1[1] + (c2[1] - c1[1]) * t)
    b = int(c1[2] + (c2[2] - c1[2]) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


class GradientBackground(tk.Canvas):
    """A Canvas subclass that paints a smooth vertical gradient and auto-redraws on resize."""

    def __init__(self, parent, top_color, bottom_color, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.top_color = top_color
        self.bottom_color = bottom_color
        self.bind("<Configure>", self._on_resize)

    def set_colors(self, top_color, bottom_color):
        self.top_color = top_color
        self.bottom_color = bottom_color
        self._draw_gradient(self.winfo_width(), self.winfo_height())

    def _on_resize(self, event):
        self._draw_gradient(event.width, event.height)

    def _draw_gradient(self, width, height):
        self.delete("gradient")
        if width <= 1 or height <= 1:
            return
        # Draw in steps rather than per-pixel for performance on large windows.
        step = 2
        for y in range(0, height, step):
            t = y / max(height - 1, 1)
            color = _interpolate_color(self.top_color, self.bottom_color, t)
            self.create_rectangle(0, y, width, y + step, outline="", fill=color, tags="gradient")
        self.tag_lower("gradient")


# ================================================================================
# SECTION 4: CHAT BUBBLE WIDGET
# --------------------------------------------------------------------------------
# Instead of a plain Text widget with two colors, each message is rendered as
# its own little rounded "bubble" using a Canvas (for the rounded rectangle)
# with a Label placed on top of it for the actual text. This is what gives the
# WhatsApp/iMessage look.
# ================================================================================

def _rounded_rect_points(x1, y1, x2, y2, radius):
    """Returns the point list needed to draw a rounded rectangle with create_polygon(..., smooth=True)."""
    return [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]


class ChatBubble(tk.Frame):
    """One chat bubble: a rounded-rectangle Canvas background + a Label with the message text."""

    def __init__(self, parent, text, timestamp, is_user, theme, wraplength=260):
        super().__init__(parent, bg=parent["bg"])

        bubble_color = theme["user_bubble"] if is_user else theme["bot_bubble"]
        text_color = theme["user_text"] if is_user else theme["bot_text"]
        border_color = None if is_user else theme["bot_bubble_border"]

        # A temporary label purely to measure how big the text will be,
        # so we can size the canvas bubble correctly around it.
        measure_font = tkfont.Font(family="Segoe UI", size=10)
        self.canvas = tk.Canvas(self, highlightthickness=0, bg=parent["bg"])
        self.canvas.pack()

        label = tk.Label(
            self.canvas, text=text, font=measure_font, bg=bubble_color, fg=text_color,
            wraplength=wraplength, justify="left", padx=12, pady=8
        )
        label.update_idletasks()
        w = min(label.winfo_reqwidth(), wraplength + 24)
        h = label.winfo_reqheight()

        self.canvas.config(width=w, height=h)
        points = _rounded_rect_points(1, 1, w - 1, h - 1, radius=14)
        self.canvas.create_polygon(
            points, smooth=True, fill=bubble_color,
            outline=(border_color or bubble_color), width=1
        )
        label.place(x=0, y=0, width=w, height=h)

        ts_label = tk.Label(
            self, text=timestamp, font=("Segoe UI", 7), bg=parent["bg"], fg=theme["timestamp"]
        )
        ts_label.pack(anchor="e" if is_user else "w", pady=(1, 0))


# ================================================================================
# SECTION 5: THE TOGGLE SWITCH (custom widget for Dark Mode)
# --------------------------------------------------------------------------------
# Tkinter has no native iOS-style toggle switch, so we draw one ourselves on a
# small Canvas: a rounded "track" plus a circular "knob" that slides left/right.
# ================================================================================

class ToggleSwitch(tk.Canvas):
    def __init__(self, parent, theme, command=None, width=46, height=24):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=parent["bg"])
        self.theme = theme
        self.command = command
        self.is_on = False
        self.w = width
        self.h = height
        self.bind("<Button-1>", self._toggle)
        self._draw()

    def _toggle(self, event=None):
        self.is_on = not self.is_on
        self._draw()
        if self.command:
            self.command(self.is_on)

    def set_theme(self, theme):
        self.theme = theme
        self.configure(bg=self.master["bg"])
        self._draw()

    def _draw(self):
        self.delete("all")
        track_color = self.theme["toggle_track_on"] if self.is_on else self.theme["toggle_track_off"]
        points = _rounded_rect_points(0, 0, self.w, self.h, radius=self.h / 2)
        self.create_polygon(points, smooth=True, fill=track_color, outline="")

        knob_d = self.h - 4
        knob_x = (self.w - self.h + 2) if self.is_on else 2
        self.create_oval(
            knob_x, 2, knob_x + knob_d, 2 + knob_d,
            fill=self.theme["toggle_knob"], outline=""
        )


# ================================================================================
# SECTION 6: MAIN APPLICATION
# --------------------------------------------------------------------------------
# Wires together the gradient background, the header (with the dark-mode
# toggle), the scrollable bubble-message area, and the input row with
# Send / Clear buttons.
# ================================================================================

class ChatbotApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.theme = LIGHT_THEME
        self.messages = []  # keeps (text, timestamp, is_user) so we can redraw on theme change

        self.root.title(f"{BOT_NAME} — Decode Labs Chatbot (Extended)")
        self.root.geometry("460x640")
        self.root.minsize(380, 480)

        # The gradient canvas is the root background; every other widget sits on top of it.
        self.bg_canvas = GradientBackground(
            self.root, self.theme["gradient_top"], self.theme["gradient_bottom"]
        )
        self.bg_canvas.pack(fill="both", expand=True)

        # A transparent-looking content frame drawn on top of the gradient canvas.
        self.content = tk.Frame(self.bg_canvas, bg=self.theme["panel_bg"])
        self.bg_canvas.create_window(0, 0, anchor="nw", window=self.content, tags="content")
        # NOTE: GradientBackground already binds its own "<Configure>" handler internally
        # (to redraw the gradient on resize). We add="+" here so BOTH handlers run,
        # instead of this second bind() silently replacing the first one.
        self.bg_canvas.bind("<Configure>", self._resize_content, add="+")

        self._build_header()
        self._build_chat_area()
        self._build_input_area()

        self._greet()

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------
    def _resize_content(self, event):
        # Keep the translucent-looking content panel matching the window size,
        # with a small margin so the gradient is visible as a "frame" around it.
        margin = 14
        self.bg_canvas.coords("content", margin, margin)
        self.bg_canvas.itemconfig(
            "content", width=event.width - margin * 2, height=event.height - margin * 2
        )

    def _build_header(self):
        self.header = tk.Frame(self.content, bg=self.theme["header_bg"], height=56)
        self.header.pack(side="top", fill="x")

        tk.Label(
            self.header, text=f"🤖  {BOT_NAME} — Chatbot",
            bg=self.theme["header_bg"], fg=self.theme["header_fg"],
            font=("Segoe UI", 13, "bold")
        ).pack(side="left", padx=14, pady=12)

        toggle_wrap = tk.Frame(self.header, bg=self.theme["header_bg"])
        toggle_wrap.pack(side="right", padx=14)
        tk.Label(
            toggle_wrap, text="Dark", bg=self.theme["header_bg"],
            fg=self.theme["header_fg"], font=("Segoe UI", 8)
        ).pack(side="left", padx=(0, 6))
        self.toggle = ToggleSwitch(toggle_wrap, self.theme, command=self._on_theme_toggle)
        self.toggle.pack(side="left")

    def _build_chat_area(self):
        wrap = tk.Frame(self.content, bg=self.theme["panel_bg"])
        wrap.pack(side="top", fill="both", expand=True, padx=6, pady=6)

        self.scroll_canvas = tk.Canvas(wrap, bg=self.theme["panel_bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(wrap, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand=scrollbar.set)

        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.bubble_frame = tk.Frame(self.scroll_canvas, bg=self.theme["panel_bg"])
        self.bubble_window = self.scroll_canvas.create_window(
            (0, 0), window=self.bubble_frame, anchor="nw"
        )

        self.bubble_frame.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        )
        self.scroll_canvas.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.itemconfig(self.bubble_window, width=e.width)
        )
        # Mouse wheel scrolling support (Windows/Mac/Linux differ slightly)
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _build_input_area(self):
        bottom = tk.Frame(self.content, bg=self.theme["panel_bg"])
        bottom.pack(side="bottom", fill="x", padx=6, pady=(0, 8))

        self.entry_font = tkfont.Font(family="Segoe UI", size=10)
        self.entry = tk.Entry(
            bottom, font=self.entry_font, relief="solid", bd=1,
            bg=self.theme["input_bg"], fg=self.theme["input_fg"],
            highlightbackground=self.theme["input_border"], highlightcolor=self.theme["input_border"]
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(4, 6))
        self.entry.bind("<Return>", lambda event: self._on_send())
        self.entry.focus_set()

        self.send_btn = tk.Button(
            bottom, text="Send", command=self._on_send,
            bg=self.theme["send_btn_bg"], fg=self.theme["send_btn_fg"],
            font=("Segoe UI", 10, "bold"), relief="flat", padx=14, pady=8, cursor="hand2"
        )
        self.send_btn.pack(side="right", padx=(0, 4))

        self.clear_btn = tk.Button(
            bottom, text="Clear", command=self._on_clear,
            bg=self.theme["clear_btn_bg"], fg=self.theme["clear_btn_fg"],
            font=("Segoe UI", 10, "bold"), relief="flat", padx=10, pady=8, cursor="hand2"
        )
        self.clear_btn.pack(side="right", padx=(0, 4))

    # ------------------------------------------------------------------
    # Behavior
    # ------------------------------------------------------------------
    def _greet(self):
        self._add_message(
            f"Hi! I'm {BOT_NAME}. Try 'help', 'joke', 'quote', 'time', or even '12*4+3'.",
            is_user=False
        )

    def _on_mousewheel(self, event):
        delta = -1 if event.delta > 0 else 1
        self.scroll_canvas.yview_scroll(delta, "units")

    def _on_send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self._add_message(text, is_user=True)

        reply = get_bot_reply(text)
        self.root.after(300, lambda: self._add_message(reply, is_user=False))

    def _on_clear(self):
        for child in self.bubble_frame.winfo_children():
            child.destroy()
        self.messages.clear()
        self._greet()

    def _add_message(self, text, is_user):
        timestamp = datetime.now().strftime("%I:%M %p")
        self.messages.append((text, timestamp, is_user))
        self._render_bubble(text, timestamp, is_user)

    def _render_bubble(self, text, timestamp, is_user):
        row = tk.Frame(self.bubble_frame, bg=self.theme["panel_bg"])
        row.pack(fill="x", pady=4, padx=6)

        bubble = ChatBubble(row, text, timestamp, is_user, self.theme)
        bubble.pack(side="right" if is_user else "left", anchor="e" if is_user else "w")

        # Auto-scroll to the bottom whenever a new message is added.
        self.bubble_frame.update_idletasks()
        self.scroll_canvas.yview_moveto(1.0)

    # ------------------------------------------------------------------
    # Theme switching (Dark Mode toggle)
    # ------------------------------------------------------------------
    def _on_theme_toggle(self, is_on):
        self.theme = DARK_THEME if is_on else LIGHT_THEME
        self._apply_theme()

    def _apply_theme(self):
        t = self.theme
        self.bg_canvas.set_colors(t["gradient_top"], t["gradient_bottom"])
        self.content.configure(bg=t["panel_bg"])
        self.header.configure(bg=t["header_bg"])
        for widget in self.header.winfo_children():
            self._restyle_recursive(widget, t)

        self.scroll_canvas.configure(bg=t["panel_bg"])
        self.bubble_frame.configure(bg=t["panel_bg"])

        self.entry.configure(bg=t["input_bg"], fg=t["input_fg"],
                              highlightbackground=t["input_border"], highlightcolor=t["input_border"])
        self.send_btn.configure(bg=t["send_btn_bg"], fg=t["send_btn_fg"])
        self.clear_btn.configure(bg=t["clear_btn_bg"], fg=t["clear_btn_fg"])
        self.toggle.set_theme(t)

        # Re-render every historical message so old bubbles pick up the new theme too.
        for child in self.bubble_frame.winfo_children():
            child.destroy()
        for text, timestamp, is_user in self.messages:
            self._render_bubble(text, timestamp, is_user)

    def _restyle_recursive(self, widget, theme):
        """Walks header sub-widgets (labels, the toggle wrapper frame) and re-applies colors."""
        try:
            widget.configure(bg=theme["header_bg"])
        except tk.TclError:
            pass
        if isinstance(widget, tk.Label):
            widget.configure(fg=theme["header_fg"])
        for child in widget.winfo_children():
            self._restyle_recursive(child, theme)


# ================================================================================
# SECTION 7: ENTRY POINT
# ================================================================================

def main():
    root = tk.Tk()
    ChatbotApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()