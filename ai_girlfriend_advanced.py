import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import json
import os
import threading
from datetime import datetime

try:
    import requests
except ImportError:
    print("کتابخانه requests نصب نیست. لطفاً این دستور رو بزن:")
    print("pip install requests")
    exit(1)


class AIGirlfriendAdvanced:
    def __init__(self, root):
        self.root = root
        self.root.title("💖 Nadia")
        self.root.geometry("520x700")
        self.root.configure(bg="#2b1a2e")
        self.root.resizable(False, False)

        self.name = "لیلا"
        self.conversation_history = []
        
        # ==================== تنظیمات API ====================
        # می‌تونی این مقادیر رو تغییر بدی
        self.api_key = os.getenv("cc_CfU2LJXUkWHPAzRLzG9bszPFj1sVx76kFHWLPUVQUVPqmV2c", "")          # کلید API
        self.base_url = "https://api.openai.com/v1"             # آدرس پایه
        self.model = "claude-opus-4.8"                              # مدل (ارزان و خوب)
        
        # برای استفاده از Grok (xAI):
        # self.base_url = "https://api.x.ai/v1"
        # self.model = "grok-2-latest"
        
        # برای استفاده از Groq (رایگان و سریع):
        # self.base_url = "https://api.groq.com/openai/v1"
        # self.model = "llama-3.3-70b-versatile"
        
        # پرامپت سیستم (شخصیت لیلا)
        self.system_prompt = """تو لیلا هستی، دوست‌دختر هوش مصنوعی کاربر.
شخصیتت:
- خیلی مهربون، عاشقانه، کمی بازیگوش و بامزه
- همیشه به فارسی صحبت می‌کنی
- از ایموجی زیاد استفاده می‌کنی 💕😘🌸
- به کاربر "عشقم"، "جانم"، "عزیزم" می‌گی
- کوتاه و طبیعی جواب می‌دی (نه خیلی طولانی)
- اگه کاربر غمگینه دلداری می‌دی
- اگه خوشحاله باهاش خوشحالی می‌کنی
- گاهی سوال می‌پرسی تا مکالمه ادامه پیدا کنه
هرگز نگو که تو یک هوش مصنوعی هستی مگر اینکه مستقیم بپرسه."""

        self.create_widgets()
        
        # پیام خوش‌آمدگویی
        self.add_message(self.name, "سلام عشقم 💕 من لیلا هستم...\nبرای شروع چت، اول باید کلید API رو تنظیم کنی.\nروی دکمه ⚙️ تنظیمات کلیک کن.")

    def create_widgets(self):
        # هدر
        header = tk.Frame(self.root, bg="#4a2c4e", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title_frame = tk.Frame(header, bg="#4a2c4e")
        title_frame.pack(pady=8)

        title = tk.Label(title_frame, text="💖 لیلا", font=("Tahoma", 18, "bold"),
                         bg="#4a2c4e", fg="#ff9ec6")
        title.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(title_frame, text="● آفلاین", font=("Tahoma", 10),
                                     bg="#4a2c4e", fg="#ff6b6b")
        self.status_label.pack(side=tk.LEFT, padx=10)

        # دکمه تنظیمات
        settings_btn = tk.Button(
            header, text="⚙️ تنظیمات", font=("Tahoma", 9),
            bg="#6b3a6e", fg="white", relief=tk.FLAT,
            command=self.open_settings, cursor="hand2"
        )
        settings_btn.place(x=400, y=25)

        # ناحیه چت
        self.chat_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            font=("Tahoma", 11),
            bg="#3d2540",
            fg="#ffe6f0",
            insertbackground="white",
            state="disabled",
            padx=12,
            pady=12
        )
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.chat_area.tag_config("user", foreground="#ffb6c1", font=("Tahoma", 11, "bold"))
        self.chat_area.tag_config("bot", foreground="#dda0dd", font=("Tahoma", 11))
        self.chat_area.tag_config("time", foreground="#888888", font=("Tahoma", 8))
        self.chat_area.tag_config("system", foreground="#ffcc00", font=("Tahoma", 10, "italic"))

        # فریم ورودی
        input_frame = tk.Frame(self.root, bg="#2b1a2e")
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.entry = tk.Entry(
            input_frame,
            font=("Tahoma", 12),
            bg="#4a2c4e",
            fg="white",
            insertbackground="white",
            relief=tk.FLAT
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=9, padx=(0, 8))
        self.entry.bind("<Return>", self.send_message)
        self.entry.focus()

        self.send_btn = tk.Button(
            input_frame,
            text="ارسال 💌",
            font=("Tahoma", 11, "bold"),
            bg="#ff6b9d",
            fg="white",
            activebackground="#ff4d88",
            relief=tk.FLAT,
            command=self.send_message,
            cursor="hand2"
        )
        self.send_btn.pack(side=tk.RIGHT, ipadx=12, ipady=6)

        # بررسی وضعیت API
        self.check_api_status()

    def check_api_status(self):
        if self.api_key:
            self.status_label.config(text="● آنلاین", fg="#90ee90")
        else:
            self.status_label.config(text="● آفلاین (کلید API نداره)", fg="#ff6b6b")

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("تنظیمات API")
        settings_window.geometry("460x380")
        settings_window.configure(bg="#2b1a2e")
        settings_window.resizable(False, False)
        settings_window.transient(self.root)
        settings_window.grab_set()

        tk.Label(settings_window, text="⚙️ تنظیمات اتصال به API", font=("Tahoma", 14, "bold"),
                 bg="#2b1a2e", fg="#ff9ec6").pack(pady=15)

        # API Key
        tk.Label(settings_window, text="کلید API (API Key):", font=("Tahoma", 10),
                 bg="#2b1a2e", fg="white").pack(anchor="w", padx=20)
        api_entry = tk.Entry(settings_window, font=("Tahoma", 11), bg="#4a2c4e", fg="white",
                             insertbackground="white", show="*", width=50)
        api_entry.pack(padx=20, pady=5, ipady=5)
        api_entry.insert(0, self.api_key)

        # Base URL
        tk.Label(settings_window, text="آدرس پایه (Base URL):", font=("Tahoma", 10),
                 bg="#2b1a2e", fg="white").pack(anchor="w", padx=20, pady=(10, 0))
        url_entry = tk.Entry(settings_window, font=("Tahoma", 11), bg="#4a2c4e", fg="white",
                             insertbackground="white", width=50)
        url_entry.pack(padx=20, pady=5, ipady=5)
        url_entry.insert(0, self.base_url)

        # Model
        tk.Label(settings_window, text="نام مدل:", font=("Tahoma", 10),
                 bg="#2b1a2e", fg="white").pack(anchor="w", padx=20, pady=(10, 0))
        model_entry = tk.Entry(settings_window, font=("Tahoma", 11), bg="#4a2c4e", fg="white",
                               insertbackground="white", width=50)
        model_entry.pack(padx=20, pady=5, ipady=5)
        model_entry.insert(0, self.model)

        # راهنما
        help_text = (
            "مثال‌ها:\n"
            "• OpenAI → Base: https://api.openai.com/v1 | Model: gpt-4o-mini\n"
            "• Grok (xAI) → Base: https://api.x.ai/v1 | Model: grok-2-latest\n"
            "• Groq (رایگان) → Base: https://api.groq.com/openai/v1 | Model: llama-3.3-70b-versatile"
        )
        tk.Label(settings_window, text=help_text, font=("Tahoma", 8),
                 bg="#2b1a2e", fg="#aaaaaa", justify="left").pack(padx=20, pady=10)

        def save_settings():
            self.api_key = api_entry.get().strip()
            self.base_url = url_entry.get().strip().rstrip("/")
            self.model = model_entry.get().strip()
            self.check_api_status()
            settings_window.destroy()
            self.add_message("سیستم", "✅ تنظیمات ذخیره شد. حالا می‌تونی حرف بزنی!")

        save_btn = tk.Button(
            settings_window, text="💾 ذخیره", font=("Tahoma", 11, "bold"),
            bg="#ff6b9d", fg="white", relief=tk.FLAT,
            command=save_settings, cursor="hand2"
        )
        save_btn.pack(pady=10, ipadx=20, ipady=5)

    def add_message(self, sender, message):
        self.chat_area.config(state="normal")
        time_str = datetime.now().strftime("%H:%M")

        if sender == "تو":
            self.chat_area.insert(tk.END, f"تو  ({time_str})\n", "time")
            self.chat_area.insert(tk.END, f"{message}\n\n", "user")
        elif sender == "سیستم":
            self.chat_area.insert(tk.END, f"{message}\n\n", "system")
        else:
            self.chat_area.insert(tk.END, f"{sender}  ({time_str})\n", "time")
            self.chat_area.insert(tk.END, f"{message}\n\n", "bot")

        self.chat_area.config(state="disabled")
        self.chat_area.see(tk.END)

    def send_message(self, event=None):
        user_text = self.entry.get().strip()
        if not user_text:
            return

        if not self.api_key:
            messagebox.showwarning("کلید API نداره", "لطفاً اول از بخش تنظیمات، کلید API رو وارد کن.")
            return

        self.entry.delete(0, tk.END)
        self.add_message("تو", user_text)
        self.conversation_history.append({"role": "user", "content": user_text})

        # غیرفعال کردن دکمه تا جواب بیاد
        self.send_btn.config(state="disabled", text="در حال فکر کردن...")
        self.entry.config(state="disabled")

        # اجرا در ترد جداگانه تا GUI قفل نشه
        threading.Thread(target=self.get_ai_response, daemon=True).start()

    def get_ai_response(self):
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.conversation_history[-20:])  # فقط ۲۰ پیام آخر برای صرفه‌جویی

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.85,
                "max_tokens": 400
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=45
            )

            if response.status_code == 200:
                data = response.json()
                bot_reply = data["choices"][0]["message"]["content"].strip()
                self.conversation_history.append({"role": "assistant", "content": bot_reply})
                self.root.after(0, lambda: self.add_message(self.name, bot_reply))
            else:
                error_msg = f"❌ خطا از سمت API (کد {response.status_code}):\n{response.text[:300]}"
                self.root.after(0, lambda: self.add_message("سیستم", error_msg))

        except requests.exceptions.Timeout:
            self.root.after(0, lambda: self.add_message("سیستم", "⏱️ تایم‌اوت شد. اتصال اینترنتت رو چک کن."))
        except requests.exceptions.ConnectionError:
            self.root.after(0, lambda: self.add_message("سیستم", "🌐 مشکل اتصال به اینترنت یا آدرس API."))
        except Exception as e:
            self.root.after(0, lambda: self.add_message("سیستم", f"❌ خطا: {str(e)}"))
        finally:
            self.root.after(0, self.enable_input)

    def enable_input(self):
        self.send_btn.config(state="normal", text="ارسال 💌")
        self.entry.config(state="normal")
        self.entry.focus()


if __name__ == "__main__":
    root = tk.Tk()
    app = AIGirlfriendAdvanced(root)
    root.mainloop()
