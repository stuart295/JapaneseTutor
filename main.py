import tkinter as tk
from tkinter import ttk, TOP, NW
import threading

from lesson_manager import LessonManager


class WordBubble(tk.Toplevel):
    def __init__(self, master, x, y, text, reset_tag):
        super().__init__(master)
        self.geometry(f"+{x}+{y}")
        self.overrideredirect(1)
        self.reset_tag = reset_tag

        ttk.Label(self, text=text, background="white", relief="solid", borderwidth=1).pack(padx=5, pady=5)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.reset_tag()
        self.destroy()


class JapanesePracticeApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.lesson = LessonManager()

        self.title("Japanese Practice App")
        self.geometry("1280x720")

        self.create_widgets()

        self.current_highlighted_tag = None

        # Start the lesson
        threading.Thread(target=self.begin_lesson).start()

    def begin_lesson(self):
        self.set_input_enabled(False)
        self.lesson.tutor.tell("[NEXT_EXERCISE]", role="assistant")
        self.show_next_sentence()
        self.set_input_enabled(True)

    def create_widgets(self):
        self.chat_frame = tk.Frame(self)
        self.chat_frame.pack(expand=True, fill="both", padx=10, pady=0)

        self.chat_log = tk.Text(self.chat_frame, wrap=tk.WORD, font=("Helvetica", 14), state="disabled")
        self.chat_log.pack(side="left", expand=True, fill="both")
        self.chat_log.tag_configure("bold", font=("Helvetica", 14, "bold"))

        self.scrollbar = ttk.Scrollbar(self.chat_frame, command=self.chat_log.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.chat_log["yscrollcommand"] = self.scrollbar.set

        self.input_frame = tk.Frame(self)
        self.input_frame.pack(expand=True, fill="x", padx=10, pady=(8, 8), side=TOP, anchor=NW)

        self.chat_input = ttk.Entry(self.input_frame, font=("Helvetica", 18))
        self.chat_input.pack(side="top", expand=True, fill="x", padx=(0, 10))
        self.chat_input.bind('<Return>', lambda event: threading.Thread(target=self.send_message).start())

        self.send_button = ttk.Button(self.input_frame, text="Send", command=lambda: threading.Thread(target=self.send_message).start(), style='TButton', width=10)
        self.send_button.pack(side="bottom", anchor="e", ipadx=10, ipady=5, pady=(8, 16), padx=10)

    def set_input_enabled(self, enabled: bool):
        if enabled:
            self.chat_input.config(state='normal')
            self.send_button.config(state='normal')
        else:
            self.chat_input.config(state='disabled')
            self.send_button.config(state='disabled')

    def send_message(self, event=None):
        message = self.chat_input.get()
        self.chat_input.delete(0, tk.END)

        # Disable the input and button
        self.set_input_enabled(False)

        # Display user input in log
        self.show_student_response(message)

        # Get and show tutor response
        self.lesson.tutor.tell(message, role="user", speaker_name="student")
        self.lesson.tutor.tell("How do you response? You can speak freely to the student. If you want to validate the student's answer to this exercise, just output the tag [CHECK]. If you want to fetch and show the next reading exercise, use the tag [NEXT_EXERCISE]", role="system")
        response = self.lesson.tutor.listen().strip()
        print(f"Tutor response:\n{response}")

        if "[CHECK]" in response:
            response = self.lesson.check_translation(message)
            print(f"Tutor checked response:\n{response}")

        if "[NEXT_EXERCISE]" in response:
            self.show_next_sentence()

        self.show_tutor_response(response.replace("[NEXT_EXERCISE]", ""))

        # Re-enable the input and button
        self.set_input_enabled(True)

    def clear_previous_tags(self):
        for tag in self.chat_log.tag_names():
            if tag.startswith("tag_ai_"):
                self.chat_log.tag_delete(tag)

    def show_next_sentence(self):
        sentence, display = self.lesson.get_next_sentence()
        self.lesson.tutor.tell(f"Please translate the following sentence: {sentence}", role="assistant")

        self.chat_log.configure(state="normal")
        self.chat_log.insert(tk.END, "Tutor\n", "bold")
        self.chat_log.insert(tk.END, "Please translate the following sentence into English:\n")

        self.clear_previous_tags()

        for index, item in enumerate(display):
            character, info = item
            tag_name = f"tag_ai_{index}"
            self.chat_log.insert(tk.END, character, tag_name)
            self.chat_log.tag_bind(tag_name, "<Button-1>", self.show_info_bubble)
            self.chat_log.tag_config(tag_name, font=("Helvetica", 14))

        self.chat_log.insert(tk.END, "\n\n")
        self.chat_log.configure(state="disabled")
        self.chat_log.see(tk.END)
        self.current_sentence = display

    def show_tutor_response(self, response: str):
        self.chat_log.configure(state="normal")
        self.chat_log.insert(tk.END, "Tutor\n", "bold")
        self.chat_log.insert(tk.END, response)

        self.chat_log.insert(tk.END, "\n\n")
        self.chat_log.configure(state="disabled")
        self.chat_log.see(tk.END)


    def show_student_response(self, message: str):
        self.chat_log.configure(state="normal")
        self.chat_log.insert(tk.END, "You\n", "bold")
        self.chat_log.insert(tk.END, f"{message}\n\n", "tag_you")
        self.chat_log.configure(state="disabled")
        self.chat_log.see(tk.END)

    def show_info_bubble(self, event):
        clicked_tag = self.chat_log.tag_names(tk.CURRENT)[0]
        tag_index_str = clicked_tag.split("_")[-1]
        if not tag_index_str.isdigit():
            print(f"Invalid tag: {clicked_tag}")
            return

        tag_index = int(tag_index_str)
        _, info_text = self.current_sentence[tag_index]

        if info_text:
            # Reset the background color of the previously highlighted tag
            if self.current_highlighted_tag:
                self.chat_log.tag_config(self.current_highlighted_tag, background="")

            try:
                self.bubble.destroy()
            except AttributeError:
                pass

            x, y, _, _ = self.chat_log.bbox(tk.CURRENT)
            x += self.chat_log.winfo_rootx()
            y += self.chat_log.winfo_rooty()

            def reset_tag():
                self.chat_log.tag_config(clicked_tag, background="")

            self.bubble = WordBubble(self, x, y - 30, info_text, reset_tag)
            self.chat_log.tag_config(clicked_tag, background="yellow")

            # Update the currently highlighted tag
            self.current_highlighted_tag = clicked_tag

        self.chat_log.configure(state="disabled")


if __name__ == "__main__":
    app = JapanesePracticeApp()
    app.mainloop()
