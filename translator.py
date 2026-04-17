import tkinter as tk
from tkinter import ttk, messagebox
from deep_translator import GoogleTranslator
from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES
from gtts import gTTS
from gtts.lang import tts_langs
import tempfile
import os
import platform
import subprocess
import time


class LanguageTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Translate Clone - B.Tech Project")
        self.root.geometry("820x620")
        self.root.minsize(820, 620)
        self.root.configure(bg="#0f172a")

        self.current_lang = "en"
        self.audio_file = None
        self.audio_process = None

        self.tts_supported = tts_langs()

        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TCombobox",
            fieldbackground="#1e293b",
            background="#1e293b",
            foreground="white",
            borderwidth=0,
            padding=8
        )

    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg="#0f172a")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header = tk.Frame(main_frame, bg="#111827", bd=0, highlightthickness=0)
        header.pack(fill="x", pady=(0, 18))

        tk.Label(
            header,
            text="🌍 Language Translator",
            font=("Segoe UI", 24, "bold"),
            bg="#111827",
            fg="white",
            pady=18
        ).pack()

        tk.Label(
            header,
            text="Translate text and listen to audio inside the app",
            font=("Segoe UI", 11),
            bg="#111827",
            fg="#cbd5e1",
            pady=2
        ).pack(pady=(0, 15))

        # Card frame
        card = tk.Frame(main_frame, bg="#1e293b", bd=0, highlightthickness=0)
        card.pack(fill="both", expand=True)

        # Input section
        tk.Label(
            card,
            text="Enter Text",
            font=("Segoe UI", 13, "bold"),
            bg="#1e293b",
            fg="white"
        ).pack(anchor="w", padx=20, pady=(20, 8))

        self.input_text = tk.Text(
            card,
            height=7,
            width=70,
            font=("Segoe UI", 11),
            bg="#0f172a",
            fg="white",
            insertbackground="white",
            relief="flat",
            wrap="word",
            padx=12,
            pady=12
        )
        self.input_text.pack(padx=20, fill="x")

        # Language row
        lang_frame = tk.Frame(card, bg="#1e293b")
        lang_frame.pack(fill="x", padx=20, pady=18)

        tk.Label(
            lang_frame,
            text="Target Language:",
            font=("Segoe UI", 11, "bold"),
            bg="#1e293b",
            fg="white"
        ).pack(side="left")

        self.lang_list = sorted(list(GOOGLE_LANGUAGES_TO_CODES.keys()))
        self.lang_combo = ttk.Combobox(
            lang_frame,
            values=self.lang_list,
            state="readonly",
            width=28,
            font=("Segoe UI", 10)
        )
        self.lang_combo.set("hindi")
        self.lang_combo.pack(side="left", padx=12)

        # Button row
        btn_frame = tk.Frame(card, bg="#1e293b")
        btn_frame.pack(fill="x", padx=20, pady=(0, 18))

        self.create_button(btn_frame, "Translate", "#2563eb", self.translate_action).pack(side="left", padx=5)
        self.create_button(btn_frame, "Speak", "#16a34a", self.speak_translation).pack(side="left", padx=5)
        self.create_button(btn_frame, "Stop", "#dc2626", self.stop_audio).pack(side="left", padx=5)
        self.create_button(btn_frame, "Clear", "#7c3aed", self.clear_text).pack(side="left", padx=5)

        # Output section
        tk.Label(
            card,
            text="Translated Output",
            font=("Segoe UI", 13, "bold"),
            bg="#1e293b",
            fg="white"
        ).pack(anchor="w", padx=20, pady=(0, 8))

        self.output_text = tk.Text(
            card,
            height=7,
            width=70,
            font=("Segoe UI", 11),
            bg="#0f172a",
            fg="#e2e8f0",
            insertbackground="white",
            relief="flat",
            wrap="word",
            padx=12,
            pady=12
        )
        self.output_text.pack(padx=20, fill="x", pady=(0, 20))

        # Footer
        footer = tk.Frame(main_frame, bg="#0f172a")
        footer.pack(fill="x", pady=(14, 0))

        tk.Label(
            footer,
            text="Made with Tkinter | B.Tech Project UI",
            font=("Segoe UI", 10),
            bg="#0f172a",
            fg="#94a3b8"
        ).pack()

    def create_button(self, parent, text, color, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=10,
            cursor="hand2"
        )

    def translate_action(self):
        source_data = self.input_text.get("1.0", tk.END).strip()
        target_lang_name = self.lang_combo.get().strip().lower()

        if not source_data:
            messagebox.showwarning("Input Error", "Please enter some text to translate.")
            return

        try:
            dest_code = GOOGLE_LANGUAGES_TO_CODES[target_lang_name]
            self.current_lang = dest_code

            translator = GoogleTranslator(source='auto', target=dest_code)
            result = translator.translate(source_data)

            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, result)

        except Exception as e:
            messagebox.showerror("Translation Error", f"Translation failed.\n{e}")

    def speak_translation(self):
        text = self.output_text.get("1.0", tk.END).strip()

        if not text:
            messagebox.showwarning("Speak Error", "No translated text available.")
            return

        try:
            self.stop_audio()
            lang_code = self.current_lang

            # fallback handling
            if lang_code not in self.tts_supported:
                if "-" in lang_code:
                    lang_code = lang_code.split("-")[0]
                elif "_" in lang_code:
                    lang_code = lang_code.split("_")[0]

            if lang_code not in self.tts_supported:
                lang_code = "en"

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            self.audio_file = temp_file.name
            temp_file.close()

            tts = gTTS(text=text, lang=lang_code)
            tts.save(self.audio_file)

            # Play audio using platform-specific method
            if platform.system() == "Windows":
                # Use default Windows media player to play MP3
                self.audio_process = subprocess.Popen(
                    ["powershell", "-NoProfile", "-Command", 
                     f"Start-Process '{os.path.abspath(self.audio_file)}'"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            elif platform.system() == "Darwin":
                # Use afplay for macOS
                self.audio_process = subprocess.Popen(["afplay", self.audio_file])
            else:
                # Use ffplay or paplay for Linux
                self.audio_process = subprocess.Popen(["ffplay", "-nodisp", "-autoexit", self.audio_file])
            
            messagebox.showinfo("Success", "Playing audio...")

        except Exception as e:
            messagebox.showerror("Speak Error", f"Could not play audio.\n{e}")

    def stop_audio(self):
        try:
            if self.audio_process:
                self.audio_process.terminate()
                self.audio_process = None
        except:
            pass

        if self.audio_file and os.path.exists(self.audio_file):
            try:
                os.remove(self.audio_file)
            except:
                pass
            self.audio_file = None

    def clear_text(self):
        self.stop_audio()
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.lang_combo.set("hindi")

    def on_close(self):
        self.stop_audio()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = LanguageTranslator(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()