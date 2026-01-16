import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import sys

class JsonViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("نمایشگر اطلاعات کاربران")
        self.root.geometry("900x600")
        
        # متغیر برای نگهداری داده‌ها
        self.data_list = []

        # --- فریم بالا (جستجو و بارگذاری) ---
        top_frame = tk.Frame(root, pady=10, padx=10)
        top_frame.pack(fill="x")

        # دکمه باز کردن فایل
        self.btn_open = tk.Button(top_frame, text="📂 باز کردن فایل JSON", command=self.load_file, bg="#e1e1e1")
        self.btn_open.pack(side="right", padx=5)

        # باکس جستجو
        tk.Label(top_frame, text="جستجو (نام کاربری):").pack(side="left")
        self.entry_search = tk.Entry(top_frame, width=30)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<KeyRelease>", self.filter_data) # جستجوی لحظه‌ای

        # --- فریم آمار ---
        stats_frame = tk.Frame(root, bg="#f0f0f0", pady=5)
        stats_frame.pack(fill="x")
        
        self.lbl_stats = tk.Label(stats_frame, text="لطفا یک فایل JSON بارگذاری کنید.", bg="#f0f0f0", font=("Arial", 10, "bold"))
        self.lbl_stats.pack()

        # --- فریم جدول ---
        table_frame = tk.Frame(root, padx=10, pady=10)
        table_frame.pack(fill="both", expand=True)

        # تعریف ستون‌ها
        columns = ("username", "name", "followers", "tweets", "bot", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # تنظیم سرستون‌ها
        self.tree.heading("username", text="نام کاربری")
        self.tree.heading("name", text="نام نمایشی")
        self.tree.heading("followers", text="فالوورها")
        self.tree.heading("tweets", text="توییت‌ها")
        self.tree.heading("bot", text="ربات؟")
        self.tree.heading("date", text="تاریخ عضویت")

        # تنظیم عرض ستون‌ها
        self.tree.column("username", width=150)
        self.tree.column("name", width=150)
        self.tree.column("followers", width=80)
        self.tree.column("tweets", width=80)
        self.tree.column("bot", width=60)
        self.tree.column("date", width=150)

        # اسکرول بار برای جدول
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # تلاش برای بارگذاری خودکار اگر فایل کنار برنامه باشد
        self.auto_load_default()

    def auto_load_default(self):
        # پیدا کردن مسیر فایل اجرایی یا اسکریپت
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        default_path = os.path.join(base_path, "IR-Network.json")
        
        if os.path.exists(default_path):
            self.process_json(default_path)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            self.process_json(file_path)

    def process_json(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.data_list = json.load(f)
            
            self.update_table(self.data_list)
            self.update_stats(self.data_list)
        except Exception as e:
            messagebox.showerror("خطا", f"فایل خوانده نشد!\n{str(e)}")

    def update_stats(self, data):
        total = len(data)
        bots = sum(1 for x in data if x.get('bot') == True)
        self.lbl_stats.config(text=f"تعداد کل کاربران: {total}  |  تعداد ربات‌ها: {bots}")

    def update_table(self, data):
        # پاک کردن جدول قبلی
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # نمایش حداکثر ۲۰۰۰ رکورد برای سرعت بالا
        for item in data[:2000]:
            is_bot = "بله" if item.get('bot') else "خیر"
            
            self.tree.insert("", "end", values=(
                item.get('username', ''),
                item.get('name', ''),
                item.get('follower_count', 0),
                item.get('number_of_tweets', 0),
                is_bot,
                item.get('creation_date', '')
            ))

    def filter_data(self, event):
        query = self.entry_search.get().lower()
        if not query:
            self.update_table(self.data_list)
            return
        
        filtered = [x for x in self.data_list if query in str(x.get('username', '')).lower()]
        self.update_table(filtered)

if __name__ == "__main__":
    root = tk.Tk()
    app = JsonViewerApp(root)
    root.mainloop()