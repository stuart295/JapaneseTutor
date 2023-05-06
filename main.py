import tkinter as tk
from tkinter import ttk, TOP, NW
import re


def gpt_4_query(prompt):
    return "TODO"


class WordBubble(tk.Toplevel):
    def __init__(self, master, x, y, text):
        super().__init__(master)
        self.geometry(f"+{x}+{y}")
        self.overrideredirect(1)

        ttk.Label(self, text=text, background="white", relief="solid", borderwidth=1).pack(padx=5, pady=5)


class JapanesePracticeApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Japanese Practice App")
        self.geometry("1280x720")

        self.create_widgets()

    def create_widgets(self):
        self.chat_frame = tk.Frame(self)
        self.chat_frame.pack(expand=True, fill="both", padx=10, pady=0)

        self.chat_log = tk.Text(self.chat_frame, wrap=tk.WORD, font=("Helvetica", 14), state="disabled")
        self.chat_log.pack(side="left", expand=True, fill="both")

        self.scrollbar = ttk.Scrollbar(self.chat_frame, command=self.chat_log.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.chat_log["yscrollcommand"] = self.scrollbar.set

        self.input_frame = tk.Frame(self)
        self.input_frame.pack(expand=True, fill="x", padx=10, pady=(8, 8), side=TOP, anchor=NW)

        self.chat_input = ttk.Entry(self.input_frame, font=("Helvetica", 18))
        self.chat_input.pack(side="top", expand=True, fill="x", padx=(0, 10))

        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_message, style='TButton', width=10)
        self.send_button.pack(side="bottom", anchor="e", ipadx=10, ipady=5, pady=(8, 16), padx=10)

    def send_message(self, event=None):
        message = self.chat_input.get()

        if message.strip():
            self.chat_log.configure(state="normal")
            self.chat_log.insert(tk.END, f"You: {message}\n", "tag_you")
            self.chat_input.delete(0, tk.END)

            response = gpt_4_query(f"Translate and provide pronunciation for the following Japanese text: {message}")
            self.chat_log.insert(tk.END, f"AI: {response}\n", "tag_ai")

            self.chat_log.tag_bind("tag_you", "<Button-1>", self.show_info_bubble)
            self.chat_log.tag_bind("tag_ai", "<Button-1>", self.show_info_bubble)
            self.chat_log.configure(state="disabled")

    def show_info_bubble(self, event):
        self.chat_log.configure(state="normal")
        word = self.chat_log.get(tk.CURRENT)
        word = re.sub('[^\w]', '', word)

        if word:
            try:
                self.bubble.destroy()
            except AttributeError:
                pass

            x, y, _, _ = self.chat_log.bbox(tk.CURRENT)
            x += self.chat_log.winfo_rootx()
            y += self.chat_log.winfo_rooty()
            info_text = f"Info for {word}"

            self.bubble = WordBubble(self, x, y - 30, info_text)
        self.chat_log.configure(state="disabled")


if __name__ == "__main__":
    app = JapanesePracticeApp()
    app.mainloop()
