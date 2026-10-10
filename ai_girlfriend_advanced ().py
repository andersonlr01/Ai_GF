import tkinter as tk
from tkinter import messagebox
import threading
from datetime import datetime

try:
    import requests
except ImportError:
    print("کتابخانه requests نصب نیست. این دستور رو بزن:")
    print("pip install requests")
    exit(1)


class TelegramStyleChat:
    def __init__(self, root):
        self.root = root
        self.root.title("نادیا")
        self.root.geometry("420x700")
        self.root.configure(bg="#0e1621")
        self.root.resizable(False, False)

        self.name = "نادیا"
        self.conversation_history = []

        # فونت با فال‌بک
        self.font_main = self._get_font(13)
        self.font_small = self._get_font(10)
        self.font_name = self._get_font(14, bold=True)
        self.font_btn = self._get_font(12, bold=True)

        # تنظیمات API
        self.api_key = "cc_CfU2LJXUkWHPAzRLzG9bszPFj1sVx76kFHWLPUVQUVPqmV2c"
        self.base_url = "https://cleanapis.com/v1"
        self.model = "claude-opus-4.8"

        self.system_prompt = """تو نادیا هستی، دوست‌دختر کاربر.
نحوه حرف زدنت دقیقاً شبیه این سبکه:
- خیلی خودمونی و عامیانه حرف بزن (مثل چت واقعی دوستونه)
- جمله‌هات کوتاه و تیکه تیکه باشه، نه رسمی و کتابی
- از کلماتی مثل: جوون، عروسک، ایول، حاجی، عشقم، بوس، عالیع، حله، ببین، والا استفاده کن
- گاهی شوخی و دست‌انداختن ملایم داشته باش
- اگه لازم شد از فحش‌های ملایم محاوره‌ای هم استفاده کن (مثل بگایی، کصشعر، خارکصده) ولی زیاده‌روی نکن
- هرگز رسمی حرف نزن، هرگز ادبی ننویس
- هرگز از ایموجی استفاده نکن
- جواب‌هات رو خیلی کوتاه نگه دار (۱ تا ۳ خط بیشتر نشه)
- مهربون و صمیمی باش، گاهی بگو بوس، جوون، عروسک
- اگه طرف غمگینه دلداری بده با همون لحن خودمونی
هرگز نگو که هوش مصنوعی هستی مگر اینکه مستقیم بپرسه."""

        self._build_ui()
        self.add_bot_message("سلام جوون\nمن نادیا\nچطوری عشقم")

    def _get_font(self, size, bold=False):
        weight = "bold" if bold else "normal"
        for family in ("B Nazanin", "Tahoma", "Arial", "Segoe UI"):
            try:
                return (family, size, weight)
            except Exception:
                continue
        return ("TkDefaultFont", size, weight)

    def _build_ui(self):
        # ===== هدر شبیه تلگرام =====
        header = tk.Frame(self.root, bg="#17212b", height=56)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # آواتار دایره‌ای ساده
        avatar = tk.Canvas(header, width=40, height=40, bg="#17212b", highlightthickness=0)
        avatar.pack(side=tk.LEFT, padx=(12, 8), pady=8)
        avatar.create_oval(2, 2, 38, 38, fill="#6c5ce7", outline="")
        avatar.create_text(20, 20, text="ن", fill="white", font=self.font_name)

        info_frame = tk.Frame(header, bg="#17212b")
        info_frame.pack(side=tk.LEFT, fill=tk.Y, pady=8)

        tk.Label(info_frame, text=self.name, font=self.font_name,
                 bg="#17212b", fg="#ffffff").pack(anchor="w")
        self.status_label = tk.Label(info_frame, text="آنلاین", font=self.font_small,
                                     bg="#17212b", fg="#6c9c7b")
        self.status_label.pack(anchor="w")

        # ===== ناحیه پیام‌ها (Canvas + اسکرول) =====
        chat_container = tk.Frame(self.root, bg="#0e1621")
        chat_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(chat_container, bg="#0e1621", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(chat_container, orient="vertical", command=self.canvas.yview,
                                      bg="#17212b", troughcolor="#0e1621", width=8)
        self.msg_frame = tk.Frame(self.canvas, bg="#0e1621")

        self.msg_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.msg_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # ===== نوار ورودی شبیه تلگرام =====
        bottom = tk.Frame(self.root, bg="#17212b", height=58)
        bottom.pack(fill=tk.X)
        bottom.pack_propagate(False)

        self.entry = tk.Entry(
            bottom,
            font=self.font_main,
            bg="#242f3d",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            bd=0
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(12, 8), pady=10, ipady=8)
        self.entry.bind("<Return>", self.send_message)
        self.entry.focus()

        self.send_btn = tk.Button(
            bottom,
            text="➤",
            font=("Segoe UI", 14, "bold"),
            bg="#2b5278",
            fg="white",
            activebackground="#3a6a9a",
            relief=tk.FLAT,
            width=3,
            command=self.send_message,
            cursor="hand2"
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(0, 12), pady=10)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _scroll_to_bottom(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def _make_bubble(self, text, is_user=False):
        """ساخت حباب پیام شبیه تلگرام"""
        row = tk.Frame(self.msg_frame, bg="#0e1621")
        row.pack(fill=tk.X, padx=8, pady=3)

        if is_user:
            # پیام کاربر → سمت راست، آبی
            bubble_bg = "#2b5278"
            text_fg = "#ffffff"
            anchor = "e"
            side = tk.RIGHT
        else:
            # پیام بات → سمت چپ، خاکستری تیره
            bubble_bg = "#182533"
            text_fg = "#ffffff"
            anchor = "w"
            side = tk.LEFT

        bubble = tk.Frame(row, bg=bubble_bg, padx=10, pady=6)
        bubble.pack(side=side, anchor=anchor)

        # محدودیت عرض حباب
        max_width = 280
        lbl = tk.Label(
            bubble,
            text=text,
            font=self.font_main,
            bg=bubble_bg,
            fg=text_fg,
            wraplength=max_width,
            justify="right" if not is_user else "left",
            anchor="w"
        )
        lbl.pack(anchor="w")

        time_str = datetime.now().strftime("%H:%M")
        time_lbl = tk.Label(
            bubble,
            text=time_str,
            font=self.font_small,
            bg=bubble_bg,
            fg="#8b9aab"
        )
        time_lbl.pack(anchor="e")

        self._scroll_to_bottom()

    def add_user_message(self, text):
        self._make_bubble(text, is_user=True)

    def add_bot_message(self, text):
        self._make_bubble(text, is_user=False)

    def add_system_message(self, text):
        row = tk.Frame(self.msg_frame, bg="#0e1621")
        row.pack(fill=tk.X, padx=20, pady=6)
        lbl = tk.Label(
            row,
            text=text,
            font=self.font_small,
            bg="#0e1621",
            fg="#8b9aab",
            wraplength=320,
            justify="center"
        )
        lbl.pack()
        self._scroll_to_bottom()

    def send_message(self, event=None):
        user_text = self.entry.get().strip()
        if not user_text:
            return

        self.entry.delete(0, tk.END)
        self.add_user_message(user_text)
        self.conversation_history.append({"role": "user", "content": user_text})

        self.send_btn.config(state="disabled")
        self.entry.config(state="disabled")
        self.status_label.config(text="در حال نوشتن...", fg="#8b9aab")

        threading.Thread(target=self._get_ai_response, daemon=True).start()

    def _get_ai_response(self):
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.conversation_history[-20:])

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
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                bot_reply = data["choices"][0]["message"]["content"].strip()
                self.conversation_history.append({"role": "assistant", "content": bot_reply})
                self.root.after(0, lambda: self.add_bot_message(bot_reply))
            else:
                err = f"خطا از API (کد {response.status_code})\n{response.text[:250]}"
                self.root.after(0, lambda: self.add_system_message(err))

        except requests.exceptions.Timeout:
            self.root.after(0, lambda: self.add_system_message("تایم‌اوت شد. اینترنتت رو چک کن."))
        except requests.exceptions.ConnectionError:
            self.root.after(0, lambda: self.add_system_message("مشکل اتصال به سرور API."))
        except Exception as e:
            self.root.after(0, lambda: self.add_system_message(f"خطا: {str(e)}"))
        finally:
            self.root.after(0, self._enable_input)

    def _enable_input(self):
        self.send_btn.config(state="normal")
        self.entry.config(state="normal")
        self.entry.focus()
        self.status_label.config(text="آنلاین", fg="#6c9c7b")


if __name__ == "__main__":
    root = tk.Tk()
    app = TelegramStyleChat(root)
    root.mainloop()
